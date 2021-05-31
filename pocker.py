"""Docker From Scratch Workshop - Level 1: Chrooting into an image.

Goal: Let's get some filesystem isolation with good ol' chroot.

Usage:
    running:
        sudo /venv/bin/python pocker.py run -i ubuntu -- bash
    will:
        fork a new child process that will:
           - unpack an ubuntu image into a new directory
           - chroot() into that directory
           - exec 'bash'
        while the parent waits for it to finish.
"""

from __future__ import print_function

import click
import os
import traceback
import tarfile
import uuid

import linux


def _get_image_path(image_name, image_dir, image_suffix='tar'):
    return os.path.join(image_dir, os.extsep.join([image_name, image_suffix]))


def _get_container_path(container_id, container_dir, *subdir_names):
    return os.path.join(container_dir, container_id, *subdir_names)


def create_container_root(image_name, image_dir, container_id, container_dir):
    """Create a container root by extracting an image into a new directory

    Usage:
    new_root = create_container_root(
        image_name, image_dir, container_id, container_dir)

    @param image_name: the image name to extract
    @param image_dir: the directory to lookup image tarballs in
    @param container_id: the unique container id
    @param container_dir: the base directory of newly generated container
                          directories
    @retrun: new container root directory
    @rtype: str
    """
    image_path = _get_image_path(image_name, image_dir)
    container_root = _get_container_path(container_id, container_dir, 'rootfs')

    assert os.path.exists(image_path), "unable to locate image %s" % image_name

    # 创建该容器的文件所在目录
    if not os.path.exists(container_root):
        os.makedirs(container_root)

    # 使用 with 自动进行文件对象的清理
    # 解压缩镜像文件压缩包到该容器目录中
    with tarfile.open(image_path) as t:
        # Fun fact: tar files may contain *nix devices! *facepalm*
        members = [m for m in t.getmembers()
                   if m.type not in (tarfile.CHRTYPE, tarfile.BLKTYPE)]
        t.extractall(container_root, members=members)

    return container_root


@click.group()
def cli():
    pass


def contain(command, image_name, image_dir, container_id, container_dir):
    new_root = create_container_root(
        image_name, image_dir, container_id, container_dir)
    print('Created a new root fs for our container: {}'.format(new_root))

    # 通过文件系统的多重挂载功能，在新的根目录下挂载 /proc、/sys
    linux.mount('proc', os.path.join(new_root, 'proc'), 'proc', 0, '')
    linux.mount('sysfs', os.path.join(new_root, 'sys'), 'sysfs', 0, '')

    # 改变容器进程的根文件系统为容器所在的目录，该函数需要root权限
    os.chroot(new_root)
    # 跳转到新的根目录下
    os.chdir('/')

    # execvp 函数能够自动从 $PATH 中寻找匹配的命令
    os.execvp(command[0], command)


@cli.command(context_settings=dict(ignore_unknown_options=True,))
@click.option('--image-name', '-i', help='Image name', default='ubuntu')
@click.option('--image-dir', help='Images directory', default='./_pocker/images')
@click.option('--container-dir', help='Containers directory', default='./_pocker/containers')
@click.argument('Command', required=True, nargs=-1)
def run(image_name, image_dir, container_dir, command):
    # 为此次启动的容器确定一个随机的 id
    contain_id = str(uuid.uuid4())
    pid = os.fork()
    if pid == 0:
        # This is the child, we'll try to do some containment here
        try:
            contain(command, image_name, image_dir, contain_id, container_dir)
        except Exception:
            traceback.print_exc()
            os._exit(1)  # something went wrong in contain()

    # This is the parent, pid contains the PID of the forked process
    # wait for the forked child and fetch the exit status
    _, status = os.waitpid(pid, 0)
    print('{} exited with status {}'.format(pid, status))


if __name__ == '__main__':
    cli()
