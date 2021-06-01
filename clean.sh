#!/usr/bin/env bash
#
# The dirtiest cleanup script
#

# umount stuff
while $(grep -q pocker /proc/mounts); do 
    sudo umount $(grep pocker /proc/mounts | shuf | head -n1 | cut -f2 -d' ') 2>/dev/null
done

# remove stuff
sudo rm -rf ./_pocker/containers/*
