---
layout: post
title:  "Linux Command Utility Guide"
date:   2023-09-14
categories: jekyll update
tags: 
  - Linux
lang: en
---

In Linux, command line utilities provide a powerful way to interact with the system, offering functionalities such as expanding disk space, file management, system monitoring, and much more. This guide will walk you through some important commands and their usage.

## Using fdisk and resize2fs to Manage Disk Partitions

Managing disk space effectively is crucial in maintaining a well-functioning system. Below are explanations and demonstrations of using `fdisk` and `resize2fs` commands to manage your disk partitions.

Below command opens the fdisk utility with administrative privileges to manage the partition table of the `/dev/sda` disk. It is a powerful tool, so it needs to be used with caution as it can alter the partition table permanently.

```
$ sudo fdisk /dev/sda

Welcome to fdisk (util-linux 2.37.2).
Changes will remain in memory only, until you decide to write them.
Be careful before using the write command.
```

The 'p' command is used to display the partition table of the disk. This can help you review the current disk setup before making any changes.

```
Command (m for help): p

Disk /dev/sda: 30 GiB, 32212254720 bytes, 62914560 sectors
Disk model: VMware Virtual S
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: gpt
Disk identifier: E2ECA603-87DC-4BEC-AF91-450E79C3CDEF

Device Start End Sectors Size Type
/dev/sda1 2048 4095 2048 1M BIOS boot
/dev/sda2 4096 1054719 1050624 513M EFI System
/dev/sda3 1054720 41940991 40886272 19.5G Linux filesystem
```

The 'd' command is used to delete a partition from the disk. This action will prompt you to enter the number of the partition you wish to delete.

```
Command (m for help): d
Partition number (1-3, default 3): 3

Partition 3 has been deleted.
```

The 'n' command is used to create a new partition on the disk. You will be guided through several steps to specify the details of the new partition, such as its size and location on the disk.

```
Command (m for help): n
Partition number (3-128, default 3): 3
First sector (1054720-62914526, default 1054720):
Last sector, +/-sectors or +/-size{K,M,G,T,P} (1054720-62914526, default 62914526):

Created a new partition 3 of type 'Linux filesystem' and of size 29.5 GiB.
Partition #3 contains a ext4 signature.

Do you want to remove the signature? [Y]es/[N]o: N
```

This prompt appears because the partition you are creating overlaps with a partition that contains a filesystem signature. Choosing 'N' means not removing the signature, which is usually the safer option to avoid potential data loss.

```
Command (m for help): w

The partition table has been altered.
Syncing disks.
```

Below command resizes the filesystem on the `/dev/sda3` partition to utilize any newly available space, especially after a partition resizing operation. This ensures that the filesystem spans the entire partition.

```
$ sudo resize2fs /dev/sda3
resize2fs 1.46.5 (30-Dec-2021)
Filesystem at /dev/sda3 is mounted on /; on-line resizing required
old_desc_blocks = 3, new_desc_blocks = 4
The filesystem on /dev/sda3 is now 7732475 (4k) blocks long.

$ df -h
Filesystem Size Used Avail Use% Mounted on
tmpfs 388M 2.1M 386M 1% /run
/dev/sda3 29G 18G 9.7G 65% /
tmpfs 1.9G 0 1.9G 0% /dev/shm
tmpfs 5.0M 4.0K 5.0M 1% /run/lock
/dev/sda2 512M 6.1M 506M 2% /boot/efi
tmpfs 388M 116K 388M 1% /run/user/1000
/dev/sr1 4.7G 4.7G 0 100% /media/luyao/Ubuntu 22.04.3 LTS amd64
/dev/sr0 156M 156M 0 100% /media/luyao/CDROM
/dev/loop15 2.4G 2.4G 0 100% /mnt/spec2006
```

Note: It is highly recommended to backup important data before manipulating disk partitions to prevent data loss.
