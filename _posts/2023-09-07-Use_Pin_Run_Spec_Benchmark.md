---
layout: post
title:  "Use Pin Run Spec Benchmark"
date:   2023-09-07
categories: jekyll update
tags: 
  - Benchmark Test 
---

## Build SPEC2006 benchmark environment
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

## Injection by Intel Pin
### Installation
```
sudo apt update
sudo apt install gcc-multilib g++-multilib libc6-dev-i386
```

### Write a demo as a target
``` cpp
#include <iostream>

void greet();
int add(int a, int b);

int main() {
    greet();
    int result = add(3, 4);
    std::cout << "The result of the addition is: " << result << std::endl;
    return 0;
}

void greet() {
    std::cout << "Hello, World!" << std::endl;
}

int add(int a, int b) {
    return a + b;
}
```
```
g++ -m32 -o demo demo.cpp
```

### Run pin to inject
Edit a pin tool:
```cpp
#include "pin.H"
#include <fstream>
#include <iostream>
#include <string>

KNOB<std::string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "pin_output.log", "specify output file name");

UINT64 icount = 0;
std::ofstream outFile;

VOID docount() { icount++; }

VOID Instruction(INS ins, VOID *v) {
    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)docount, IARG_END);
}

VOID Fini(INT32 code, VOID *v) {
    outFile.open(KnobOutputFile.Value().c_str(), std::ios::out);
    if(outFile.is_open()) {
        outFile << "Count " << icount << std::endl;
        outFile.close();
    } else {
        std::cerr << "Could not open log file" << std::endl;
    }
}

int main(int argc, char *argv[]) {
    if (PIN_Init(argc, argv)) return -1;

    INS_AddInstrumentFunction(Instruction, 0);
    PIN_AddFiniFunction(Fini, 0);

    PIN_StartProgram();
    return 0;
}
```

Compile this tool and run pin:
```
cd source/tools/MyPinTool/
make clean
make TARGET=ia32
pin -t obj-ia32/MyPinToolForTest.so -o my_log_file.log -- ./demo
```

### Result
```
$ pin -t obj-ia32/MyPinToolForTest.so -- /home/luyao/research/test/demo
Hello, World!
The result of the addition is: 7
Count 2367254
```
