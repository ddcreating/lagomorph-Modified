raise Exception("DEPRECATED: This example has not been updated to use the new pytorch interface")

import torch
import torch.distributed as dist
import h5py
import numpy as np
import lagomorph.torch as lt
import math
from tqdm import tqdm
import atexit


if __name__ == '__main__':
    from mpi4py import MPI

    use_mpi = True

    comm = MPI.COMM_WORLD
    world_size = comm.Get_size()
    rank = comm.Get_rank()
    atexit.register(MPI.Finalize)

    num_local_gpus = 1

    dist.init_process_group(backend="mpi",
                            init_method="file:///tmp/distributed_test",
                            world_size=world_size,
                            rank=rank)

    border=0

    w = 128
    with h5py.File(f'/raid/ChestXRay14/chestxray14_{w}.h5', 'r') as f:
        train_imgs = f['/images/train'][:65000,...]
        num_samples = train_imgs.shape[0]
        # determine how many (max) examples per device
        total_gpus = num_local_gpus * world_size
        samples_per_gpu = (num_samples + total_gpus - 1)//total_gpus
	# I crop the boundary pixels out since they are often introduce discontinuities
        for d in range(world_size*rank,num_local_gpus,world_size):
            start = (rank*num_local_gpus + d)*samples_per_gpu
            end = start + samples_per_gpu
            if border > 0:
                sl = train_imgs[start:end, border:-border, border:-border]
            else:
                sl = train_imgs[start:end, ...]
            Jhost = np.asarray(sl, dtype=np.float32)/255.0
            Js.append(torch.from_numpy(Jhost).cuda(d, non_blocking=True))

    # atlas params
    use_contrast = False
    diagonal = True
    regA = regT = 1e-3
    #interp = lt.AffineInterpImage()
    interp = lt.AffineInterpImageFunction.apply
    A = J.new_zeros((J.size(0), 2, 2))
    A[:,0,0] = 1.
    A[:,1,1] = 1.
    T = J.new_zeros((J.size(0), 2))
    # initialize image is just arithmetic mean of inputs
    I = J.sum(dim=0, keepdim=True)/num_samples
    dist.all_reduce(I)
    atlas_iters = 100
    base_image_iters = 10
    match_iters = 100
    base_image_stepsize = 1e2
    stepsize_A = 1e2
    stepsize_T = 1e5
    criterion = torch.nn.MSELoss()
    it_losses = []
    report = rank == 0
    with tqdm(total=atlas_iters,desc=f'Atlas', position=0, disable=not report) as tatlas, \
         tqdm(total=match_iters,desc=f'Match', position=1, disable=not report) as tmatch, \
         tqdm(total=base_image_iters,desc=f'Image', position=2, disable=not report) as timage:
        for ait in range(atlas_iters):
            # reset progress bars
            tmatch.n = timage.n = 0
            tmatch.refresh(), timage.refresh()
            I = torch.autograd.Variable(I, requires_grad=False)
            A = torch.autograd.Variable(A, requires_grad=True)
            T = torch.autograd.Variable(T, requires_grad=True)
            optimizer = torch.optim.SGD([{'params':[A], 'lr':stepsize_A},
                            {'params':[T], 'lr':stepsize_T}], momentum=0.0)
            for mit in range(match_iters):
                optimizer.zero_grad()
                optimizers.append(optimizers)
                Itx = interp(I, A, T)
                loss = criterion(Itx, J)
                loss.backward()
                optimizer.step()
                dist.reduce(losses, 0)
                lossi = loss.item()
                it_losses.append(lossi)
                tmatch.set_postfix({'loss':lossi})
                tmatch.update()
            # update base image iteratively
            I = torch.autograd.Variable(I, requires_grad=True)
            A = torch.autograd.Variable(A, requires_grad=False)
            T = torch.autograd.Variable(T, requires_grad=False)
            # TODO: use custom Jacobi method function here instead of fixed GD
            for bit in range(base_image_iters):
                Itx = interp(I, A, T)
                loss = criterion(Itx, J)
                gI, = torch.autograd.grad(loss, I)
                I = I/world_size - base_image_stepsize * gI
                dist.all_reduce(I)
                dist.reduce(loss, 0)
                lossi = loss.item()
                it_losses.append(lossi)
                timage.set_postfix({'loss':lossi})
                timage.update()
            tatlas.set_postfix({'rel_loss': lossi/it_losses[0], 'loss':lossi})
            tatlas.update()
