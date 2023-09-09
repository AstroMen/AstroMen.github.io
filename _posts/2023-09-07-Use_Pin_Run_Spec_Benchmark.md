---
layout: post
title:  "Use Pin Run Spec Benchmark"
date:   2023-09-07
categories: jekyll update
tags: 
  - Benchmark Test 
---

### Install apt package
```shell
sudo apt update
sudo apt install build-essential
sudo apt install libc6:i386 libncurses5:i386 libstdc++6:i386
sudo apt install gcc-multilib
```

### Install SPEC and build benchmark
```shell
cd /mnt
sudo mkdir -p /mnt/spec2006
sudo mount -o loop path_to_your_spec2006.iso /mnt/spec2006

cd /mnt/spec2006
./install.sh -d /home/user/SPEC2006 -u linux-suse101-i386

vim ~/.bashrc 
source ~/.bashrc
  
cd /home/user/SPEC2006/
source shrc
runspec --action=build --config=Example-linux32-i386-gcc42.cfg --tune=base bzip2
runspec --action=build --config=Example-linux64-amd32-gcc42.cfg --tune=base bzip2
```

### Run benchmark
```
runspec --config=Example-linux64-amd32-gcc42.cfg 400.perlbench
```
Result:
```
Producing Raw Reports
mach: default
  ext: amd64-m32-gcc42-nn
    size: ref
      set: int
        format: raw -> /home/user/SPEC2006/result/CINT2006.019.ref.rsf
Parsing flags for 400.perlbench base: done
Doing flag reduction: done
        format: flags -> /home/user/SPEC2006/result/CINT2006.019.ref.flags.html
        format: ASCII -> /home/user/SPEC2006/result/CINT2006.019.ref.txt
        format: PDF -> /home/user/SPEC2006/result/CINT2006.019.ref.pdf
        format: Screen -> 
                                  Estimated                       Estimated
                Base     Base       Base        Peak     Peak       Peak
Benchmarks      Ref.   Run Time     Ratio       Ref.   Run Time     Ratio
-------------- ------  ---------  ---------    ------  ---------  ---------
400.perlbench    9770        340       28.8 *                                  
401.bzip2                                   NR                                 
403.gcc                                     NR                                 
429.mcf                                     NR                                 
445.gobmk                                   NR                                 
456.hmmer                                   NR                                 
458.sjeng                                   NR                                 
462.libquantum                              NR                                 
464.h264ref                                 NR                                 
471.omnetpp                                 NR                                 
473.astar                                   NR                                 
483.xalancbmk                               NR                                 
 Est. SPECint_base2006                   --
 Est. SPECint2006                                                   Not Run

      set: fp

The log for this run is in /home/user/SPEC2006/result/CPU2006.019.log
```
