#!/bin/bash

echo "🔍 当前 Conda 环境: $CONDA_PREFIX"
if [ -z "$CONDA_PREFIX" ]; then
  echo "❌ 请先激活你的 Conda 环境再运行此脚本"
  exit 1
fi

echo "🧼 卸载旧版本 torch/torchvision/torchaudio ..."
pip uninstall -y torch torchvision torchaudio

echo "🧹 清理 site-packages 中残留的 torch 文件 ..."
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
rm -rf $SITE_PACKAGES/torch*
rm -rf $SITE_PACKAGES/torchvision*
rm -rf $SITE_PACKAGES/torchaudio*

echo "✅ 清理完成，开始重新安装 PyTorch 2.0.1 + cu118 ..."
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2 \
  --extra-index-url https://download.pytorch.org/whl/cu118

echo "✅ 安装完成！当前版本："
python -c "import torch; print('Torch:', torch.__version__, '| CUDA:', torch.version.cuda, '| CUDA 可用:', torch.cuda.is_available())"
