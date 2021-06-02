# Pocker

用 Python 写的一个迷你容器

## startup

需要 python3、docker，以下操作都在本项目根路径下执行

``` shell

# 创建容器的辅助目录
mkdir -p _pocker/containers
mkdir -p _pocker/images

# 导出 docker 基础镜像文件 Ubuntu
docker pull ubuntu
docker run -d ubuntu /bin/bash -c 'apt-get update && apt-get install -y stress net-tools'
docker export -o ubuntu.tar <container-id>
mv ubuntu.tar _pocker/images/

# 使用 python 虚拟环境
virtualenv venv
source venv/bin/activate

# 安装 pocker 依赖
pip install -r requirements.txt

# 安装 python 的 c 扩展，提供一些 python 库中原先不支持的 api
python setup.py install

# 使用 root 权限运行容器
sudo /venv/bin/python pocker.py run -i ubuntu bash

```

## 功能

1. 改变进程根目录 chroot/piovt_root，限制进程访问文件的范围
2. COW 文件系统 overlayfs，复用镜像文件，使容器轻量化
3. 资源隔离 namespace
    1. mount CLONE_NEWNS 容器内部的挂载不会传播到 host
    2. hostname CLONE_NEWUTS 独立的域名和主机名
    3. pid CLONE_NEWPID 容器内部的进程拥有独立的编号，不能看见 host 的进程
    4. net CLONE_NEWNET 网络资源的隔离，
4. 资源限制 cgroup，通过操作 `/sys/fs/cgroup/` 下的文件
    1. cpu
    2. mem

## TODO

1. 支持 image 和 container 的更多操作，目前只能 run image
2. 更完全的 ns 隔离，更多的 cgroup 控制选项
