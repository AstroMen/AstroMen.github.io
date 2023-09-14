---
layout: post
title:  "Guide to Setting Up and Executing the SPEC2006 Benchmark with Intel Pin Injection"
date:   2023-09-07
categories: jekyll update
tags: 
  - Benchmark Test 
---

## Step 1: Building the SPEC2006 Benchmark Environment
### Install Necessary Packages
Before you proceed, make sure you have the necessary packages installed on your system by running the following commands in your terminal:
```shell
sudo apt update
sudo apt install build-essential
sudo apt install libc6:i386 libncurses5:i386 libstdc++6:i386
sudo apt install gcc-multilib
```

### Install SPEC and Build Benchmark
Install SPEC and setup the benchmark environment using the following commands:
```shell
cd /mnt
sudo mkdir -p /mnt/spec2006
sudo mount -o loop path_to_your_spec2006.iso /mnt/spec2006

cd /mnt/spec2006
./install.sh -d /home/user/SPEC2006 -u linux-suse101-i386
```

### Set environment variable
Next, edit your environment variable file to set the necessary paths:
1. Open the file using a text editor: `vim ~/.bashrc`.
2. Add the following content:
```
# SPEC2006
cpu2006=/home/user/research/SPEC2006
export PATH=$cpu2006/bin:$PATH
export PATH=$cpu2006/shrc:$PATH
```
3. Save and exit the editor.
4. Apply the changes: `source ~/.bashrc`.

### Build the Benchmark
Navigate to the SPEC2006 directory and build the benchmark using these commands:
```
cd /home/user/SPEC2006/
source shrc
runspec --action=build --config=Example-linux32-i386-gcc42.cfg --tune=base bzip2
runspec --action=build --config=Example-linux64-amd32-gcc42.cfg --tune=base bzip2
```

### Run benchmark
To run the benchmark, use the following command and review the generated result:
```
runspec --config=Example-linux64-amd32-gcc42.cfg 400.perlbench
```
The result will be displayed in the terminal, similar to the example given in your original document.
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

## Step 2: Injection using Intel Pin
### Installation
Update your system and install necessary packages:
```
sudo apt update
sudo apt install gcc-multilib g++-multilib libc6-dev-i386
```

### Set Environment Variables
Set up environment variables for the Intel Pin:
```
# PIN
export PIN_ROOT=/home/user/research/pin
export PATH=$PIN_ROOT:$PATH
```

### Create a Demo Target Program
Write a simple C++ program as a demo target for the pin injection:
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
Compile the program using the following command:
```
g++ -m32 -o demo demo.cpp
```

### Create and Compile a Pin Tool
Create a pin tool with the following C++ code:
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

Navigate to the MyPinTool directory, clean any existing build files, and compile the tool:
```
cd source/tools/MyPinTool/
make clean
make TARGET=ia32
```

### Run Pin to Inject
To run the pin and inject into the demo, use the following commands:
```
pin -t obj-ia32/MyPinToolForTest.so -o my_log_file.log -- ./demo
```

### View Results
After running the pin, you should see an output similar to:
```
$ pin -t obj-ia32/MyPinToolForTest.so -- ~/research/test/demo
Hello, World!
The result of the addition is: 7
Count 2367254
```

### Additional Injection Examples
You can also perform injection with specinvoke using commands like:
```
pin -t ~/research/pin/source/tools/MyPinToolForTest/obj-ia32/MyPinToolForTest.so -o ~/research/pin/source/tools/MyPinToolForTest/pin_output_bzip2_specinvoke_amd.log -- specinvoke -c Example-linux32-i386-gcc42 -d ~/research/SPEC2006/benchspec/CPU2006/401.bzip2/exe/ -e error.log -o output.log -f instructions.txt
```

Ensure that the instructions.txt file contains the following line:
```
~/research/SPEC2006/benchspec/CPU2006/401.bzip2/exe/bzip2_base.amd64-m32-gcc42-nn -i ~/research/SPEC2006/benchspec/CPU2006/401.bzip2/data/all/input/input.combined
```
