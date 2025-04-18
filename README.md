# lagomorph-Modified

This repository contains the modified **Lagomorph** library, updated for compatibility with **PyTorch >= 1.1.0** and **CUDA**.

Link to the original version: [jacobhinkle/lagomorph](https://github.com/jacobhinkle/lagomorph/tree/master)

# Installation

1. Clone or download the modified Lagomorph repository.

2. Open a terminal and navigate to the folder containing `setup.py`.

3. Run the following command to install the library in "editable" mode:

```
pip install -e . --no-build-isolation

```

This will pull in the following prerequisites:

- **PyTorch >= 1.1.0**
- **NumPy < 2.0**

**PyTorch:** Ensure you have a compatible version of **PyTorch >= 1.1.0** installed. You can install **PyTorch 2.1.1+cu121** with:  `pip install torch==2.1.1+cu121 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`

**numpy:** Note that often it is necessary to install `numpy` manually first using `pip install numpy` due to weirdness in numpy's packaging.

**CUDA:** Ensure your environment has a compatible **CUDA** version. In this repository, **CUDA 12.8** is used with **PyTorch 2.1.1+cu121**. However, other versions of CUDA that are compatible with your PyTorch version should work as well.

To run the test suite for lagomorph, execute the following command from the current directory in this repository:

```
python setup.py test

```

## Notes

- The installation is tested with **PyTorch 2.1.1+cu121** and **CUDA 12.8**, but other compatible versions of PyTorch and CUDA should work.
