# Ensure system is updated and has my toolkit
sudo apt-get update
sudo apt-get --assume-yes install tmux vim zsh git curl openssh-server build-essential gcc g++ make cmake binutils software-properties-common graphviz unzip

# install miniconda (silently)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -f
export PATH="/root/miniconda3/bin:$PATH"
conda init bash
source /root/.bashrc

# env vars for linode bucket
export AWS_ACCESS_KEY_ID='FIWP07U3W9YBOIC4UGYY'
export AWS_SECRET_ACCESS_KEY='ILY6MT2as4wQp0tVZ08bZm2TM0O1T6XhiYHgc4cR'
export REGION_NAME='us-east-1'
export AWS_S3_ENDPOINT='linodeobjects.com'
export AWS_BUCKET_NAME='vln-bert'

# env vars for comet
export COMET_API_KEY='kzXOEnh77cj97a8H89yH2hDgq'

# create venv
conda create -y -n vlnbert python=3.6
conda activate vlnbert

# download code
cd
git clone https://github.com/ceyzaguirre4/vln-bert.git

# install vlnbert specific package
cd
cd vln-bert
conda install  -y pytorch torchvision torchaudio cudatoolkit=10.2 -c pytorch
pip install -r requirements.txt

# download training data, features and pretrained weights
python s3_utils.py
unzip data.zip
unzip matterport-ResNet-101-faster-rcnn-genome.lmdb.zip
mv matterport-ResNet-101-faster-rcnn-genome.lmdb data/matterport-ResNet-101-faster-rcnn-genome.lmdb

# # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # TRAIN # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # #

# load multi-task and pretrain on VLN
python train.py \
--from_pretrained multi_task_model.bin \
--save_name multi_task \
--num_epochs 50 \
--warmup_proportion 0.08 \
--cooldown_factor 8 \
--masked_language \
--masked_vision \
--no_ranking

# load multitask + pretrained and train for training
python train.py \
--from_pretrained data/runs/run-multi_task/pytorch_model_best_unseen.bin \
--save_name multi_task_final
