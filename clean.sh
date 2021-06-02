#!/usr/bin/env bash
#
# The dirtiest cleanup script
#

# umount stuff
while $(grep -q pocker /proc/mounts); do 
    sudo umount $(grep pocker /proc/mounts | shuf | head -n1 | cut -f2 -d' ') 2>/dev/null
done

# remove stuff
for dir in `ls ./_pocker/containers/`
do
    # remove container
    sudo rm -rf "./_pocker/containers/${dir}"

    # remove cpu cgroup
    if [ -d "/sys/fs/cgroup/cpu/pocker/${dir}" ]; then
        sudo rmdir "/sys/fs/cgroup/cpu/pocker/${dir}"
    fi
    
    # remove memory cgroup
    if [ -d "/sys/fs/cgroup/memory/pocker/${dir}" ]; then
        sudo rmdir "/sys/fs/cgroup/memory/pocker/${dir}"
    fi
done