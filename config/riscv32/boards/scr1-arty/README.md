# A Board Configuration for Syntacore SCR1 for Xilinx Arty Board

Author: Hiroo HAYASHI

Copyright (C) 2021 Hiroo HAYASHI

This document is part of Embench.
It is made freely available under the terms of the GNU Free Documentation
License version 1.2 or later.

Embench is a trade mark of the Embench Task Group of the Free and Open Source
Silicon Foundation.

***

This configuration demonstrates how to run the Embench on an FPGA board.
No performance tuning is done.  Your contributions are welcome.

## Requirements

- [Digilent Arty A7 100T Reference board](https://digilent.com/reference/programmable-logic/arty-a7/start)
- [SCR1 RISC-V Core](https://github.com/syntacore/scr1#scr1-risc-v-core)
- [SCR1 SDK. Xilinx Vivado Design Suite project for Arty board](https://github.com/syntacore/fpga-sdk-prj/tree/master/arty/scr1#scr1-sdk-xilinx-vivado-design-suite-project-for-arty-board)
- [Open-source SDK for SCR1 core](https://github.com/syntacore/scr1-sdk#open-source-sdk-for-scr1-core)
- [SW development tools](https://syntacore.com/page/products/sw-tools)
- [syntacore/openocd](https://github.com/syntacore/openocd/releases)

## Configuring FPGA

Follow the instruction in  [SCR1 SDK. Xilinx Vivado Design Suite project for Arty board](https://github.com/syntacore/fpga-sdk-prj/tree/master/arty/scr1#scr1-sdk-xilinx-vivado-design-suite-project-for-arty-board).

## Running Embench

### Preparations

Add the `bin/` directory of [SW development tools](https://syntacore.com/page/products/sw-tools) on the environment variables `PATH`.

Set the environment variable `SCR1_SDK_PATH` to the directory of the SCR1 SDK installed. For example;

  ```sh
  export SCR1_SDK_PATH=$HOME/github/scr1-sdk
  ```

Build some object files in SDK.

```sh
cd $SCR1_SDK_PATH
make -C sw/hello OPT_CFLAGS="-O2 -g"
```

`-g` is required to set a breakpoint in GDB.

### Running the benchmark of code size

Benchmarks should be compiled with dummy versions of all standard libraries.

```sh
./build_all.py -v --arch riscv32 --chip generic --board scr1-arty \
    --cflags "-Os -msave-restore" --dummy-libs "crt0 libc libgcc libm"
./benchmark_size.py
```

In the above examples, `-Os -msave-restore` is used for `--cflags` to get
size-optimized results. Use `-O2` or other options to get the
performance-optimized results.

### Running the benchmark of code speed

Invoke an OpenOCD server in a terminal window.

```sh
/opt/syntacore/openocd-0.10.0-1974/bin/openocd \
    -f interface/ftdi/olimex-arm-usb-ocd-h.cfg \
    -f target/syntacore_riscv.cfg
```

Run the following command in a terminal window.
(The device name `/dev/ttyUSB1` may be different on your system.)

```sh
minicom -b 115200 -D /dev/ttyUSB1
```

Build and run the benchmark.
Benchmarks should be compiled with real versions of libraries in the SDK.

```sh
./build_all.py -v --arch riscv32 --chip generic --board scr1-arty \
    --cflags "-Os -msave-restore -I$SCR1_SDK_PATH/sw/hello/common" \
    --ldflags "$SCR1_SDK_PATH/sw/hello/build.arty_scr1.tcm.o2/common/printf.o \
        $SCR1_SDK_PATH/sw/hello/build.arty_scr1.tcm.o2/common/syscalls.o \
        $SCR1_SDK_PATH/sw/hello/build.arty_scr1.tcm.o2/common/nlib.o \
        $SCR1_SDK_PATH/sw/hello/build.arty_scr1.tcm.o2/common/uart.o \
        $SCR1_SDK_PATH/sw/hello/build.arty_scr1.tcm.o2/common/ncrt0.o" \
    --user-libs "-Wl,--start-group -lc -lgcc -lm -Wl,--end-group"
./benchmark_speed.py --target-module run_scr1-arty
```

## Debugging

### Debugging with GDB

Rebuild with compile option "-O -g".

Example:

```sh
... <invoke an OpenOCD server (See above)> ...
$ cat gdbconf
sset confirm off
set remotetimeout 240
target extended-remote localhost:3333
monitor reset halt
load
break exit
$ riscv64-unknown-elf-gdb -q -x gdbconf bd/src/md5sum/md5sum
...
(gdb) j _start
...
```

Use `load` command to reload a recompiled program.
