# Installation Instructions

### Setup Anaconda Virtual Environment
The instructions below are a summarized version from [Anaconda Install Instructions](https://conda.io/docs/user-guide/install/index.html)


```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
wget https://repo.continuum.io/archive/Anaconda3-2018.12-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
bash Anaconda-latest-Linux-x86_64.sh
```
Follow the installation instructions. Once done, restart the terminal so the changes make effect.

Test your installation by running
```bash
conda list
```


### Create a virtual env and setup a Python version
```bash
conda create -n economics python=3.7
source activate economics
```
    
### Install requirements
```bash
cd auction/
pip install -r requirements.txt --ignore-installed
```

### Running the code


     
    
