## Installation

### Code installation

#### Install with pip
```shell
# 1. Create anaconda environment
conda create -n body_head_recovery python=3.10
conda activate body_head_recovery

# 2. Install requirement
pip install -r requirement.txt

# 3. Install PyTorch
pip install torch==2.2.1 torchvision==0.17.1 torchaudio==2.2.1 --index-url https://download.pytorch.org/whl/cu118

# 4. Install Pytorch3D
#https://github.com/facebookresearch/pytorch3d/blob/main/INSTALL.md
pip install "git+https://github.com/facebookresearch/pytorch3d.git@stable"

### Models
1. Download the reconstruction model manually: ** .pt** ([Google Drive](https://drive.google.com/drive/folders/1cUPP0z06Bb41OiWrLwLBXxZmJRIz7t4h?usp=drive_link)). Place it into `models/jits/` folder.
2. Download the smplx model: **smplx_models** ([Google Drive](https://drive.google.com/drive/folders/1apRPQW_IDKZ6BQOH53_XuOjMjl8he1kW?usp=drive_link)). Place it into `models/smplx/` folder.
3. Download the face lmks model: **face lmks** ([Google Drive](https://drive.google.com/file/d/1Z0Xe_Rwm8GGCThy21rjdoBhFwcXxRiHZ/view?usp=drive_link)). Place it into `models/` folder.

## Running

python main_test.py"# body_head_recovery" 
# try-on-ai-ml
