#!/usr/bin/env python3

# Script to build and run all benchmarks

# Copyright (C) 2017, 2019 Embecosm Limited
#
# Contributor: Graham Markall <graham.markall@embecosm.com>
# Contributor: Jeremy Bennett <jeremy.bennett@embecosm.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Run sets of Embench benchmarks
"""


import argparse
import os
import shutil
import subprocess
import sys

sys.path.append(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'pylib')
)

from embench_core import check_python_version
from embench_core import log
from embench_core import gp
from embench_core import setup_logging
from embench_core import log_args
from embench_core import find_benchmarks
from embench_core import log_benchmarks
from embench_core import arglist_to_str

# The various sets of benchmarks we could run

fosdem_rv32_gcc_opt_runset = {
    'name' : 'FOSDEM RV32IMC optimization comparison',
    'size benchmark' : {
        'timeout' : 30,
        'arglist' : [
            './benchmark_size.py',
            '--json-output',
        ],
        'desc' : 'sized'
    },
    'speed benchmark' : {
        'timeout' : 1800,
        'arglist' : [
            './benchmark_speed.py',
            '--target-module=run_gdbserver_sim',
	    '--gdbserver-command=riscv32-gdbserver',
	    '--gdb-command=riscv32-unknown-elf-gdb',
            '--json-output',
        ],
        'desc' : 'run'
    },
    'runs' : [
        { 'name' : 'fosdem-rv32-gcc-opt-o0',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O0',
          'ldflags' : '',
          'path' : 'install-gcc',
        },
        { 'name' : 'fosdem-rv32-gcc-opt-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'ldflags' : '',
          'path' : 'install-gcc',
        },
        { 'name' : 'fosdem-rv32-gcc-opt-og',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Og',
          'ldflags' : '',
          'path' : 'install-gcc',
        },
        { 'name' : 'fosdem-rv32-gcc-opt-o1',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O1',
          'ldflags' : '',
          'path' : 'install-gcc',
        },
        { 'name' : 'fosdem-rv32-gcc-opt-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'ldflags' : '',
          'path' : 'install-gcc',
        },
        { 'name' : 'fosdem-rv32-gcc-opt-o3',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O3',
          'ldflags' : '',
          'path' : 'install-gcc',
        },
    ]
}

fosdem_rv32_llvm_opt_runset = {
    'name' : 'FOSDEM RV32IMC optimization comparison',
    'size benchmark' : {
        'timeout' : 30,
        'arglist' : [
            './benchmark_size.py',
            '--json-output',
        ],
        'desc' : 'sized'
    },
    'speed benchmark' : {
        'timeout' : 1800,
        'arglist' : [
            './benchmark_speed.py',
            '--target-module=run_gdbserver_sim',
	    '--gdbserver-command=riscv32-gdbserver',
	    '--gdb-command=riscv32-unknown-elf-gdb',
            '--json-output',
        ],
        'desc' : 'run'
    },
    'runs' : [
        { 'name' : 'fosdem-rv32-llvm-opt-o0',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-clang',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O0',
          'ldflags' : '',
          'path' : 'install-llvm',
        },
        { 'name' : 'fosdem-rv32-llvm-opt-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-clang',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'ldflags' : '',
          'path' : 'install-llvm',
        },
        { 'name' : 'fosdem-rv32-llvm-opt-oz-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-clang',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Oz -msave-restore',
          'ldflags' : '',
          'path' : 'install-llvm',
        },
        { 'name' : 'fosdem-rv32-llvm-opt-o1',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-clang',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O1',
          'ldflags' : '',
          'path' : 'install-llvm',
        },
        { 'name' : 'fosdem-rv32-llvm-opt-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-clang',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'ldflags' : '',
          'path' : 'install-llvm',
        },
        { 'name' : 'fosdem-rv32-llvm-opt-o3',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-clang',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O3',
          'ldflags' : '',
          'path' : 'install-llvm',
        },
    ]
}

fosdem_arm_gcc_opt_runset = {
    'name' : 'FOSDEM Arm Cortex M4 optimization comparison',
    'size benchmark' : {
        'timeout' : 30,
        'arglist' : [
            './benchmark_size.py',
            '--json-output',
        ],
        'desc' : 'sized'
    },
    'runs' : [
        { 'name' : 'fosdem-arm-gcc-opt-o0',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -O0',
          'ldflags' : '',
          'path' : 'install-gcc-arm',
        },
        { 'name' : 'fosdem-arm-gcc-opt-os',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -Os',
          'ldflags' : '',
          'path' : 'install-gcc-arm',
        },
        { 'name' : 'fosdem-arm-gcc-opt-og',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -Og',
          'ldflags' : '',
          'path' : 'install-gcc-arm',
        },
        { 'name' : 'fosdem-arm-gcc-opt-o1',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -O1',
          'ldflags' : '',
          'path' : 'install-gcc-arm',
        },
        { 'name' : 'fosdem-arm-gcc-opt-o2',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -O2',
          'ldflags' : '',
          'path' : 'install-gcc-arm',
        },
        { 'name' : 'fosdem-arm-gcc-opt-o3',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -O3',
          'ldflags' : '',
          'path' : 'install-gcc-arm',
        },
    ]
}

fosdem_arm_llvm_opt_runset = {
    'name' : 'FOSDEM Arm Cortex M4 optimization comparison',
    'size benchmark' : {
        'timeout' : 30,
        'arglist' : [
            './benchmark_size.py',
            '--json-output',
        ],
        'desc' : 'sized'
    },
    'runs' : [
        { 'name' : 'fosdem-arm-llvm-opt-o0',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-clang',
          'cflags' : ('-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -O0 --sysroot=' +
                      os.path.abspath(os.path.join(
                          os.path.dirname(__file__),
                          os.pardir,
                          'install-llvm-arm/arm-none-eabi'))),
          'ldflags' : '-fuse-ld=bfd',
          'path' : 'install-llvm-arm',
        },
        { 'name' : 'fosdem-arm-llvm-opt-os',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-clang',
          'cflags' : ('-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -Os --sysroot=' +
                      os.path.abspath(os.path.join(
                          os.path.dirname(__file__),
                          os.pardir,
                          'install-llvm-arm/arm-none-eabi'))),
          'ldflags' : '-fuse-ld=bfd',
          'path' : 'install-llvm-arm',
        },
        { 'name' : 'fosdem-arm-llvm-opt-oz',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-clang',
          'cflags' : ('-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -Oz --sysroot=' +
                      os.path.abspath(os.path.join(
                          os.path.dirname(__file__),
                          os.pardir,
                          'install-llvm-arm/arm-none-eabi'))),
          'ldflags' : '-fuse-ld=bfd',
          'path' : 'install-llvm-arm',
        },
        { 'name' : 'fosdem-arm-llvm-opt-o1',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-clang',
          'cflags' : ('-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -O1 --sysroot=' +
                      os.path.abspath(os.path.join(
                          os.path.dirname(__file__),
                          os.pardir,
                          'install-llvm-arm/arm-none-eabi'))),
          'ldflags' : '-fuse-ld=bfd',
          'path' : 'install-llvm-arm',
        },
        { 'name' : 'fosdem-arm-llvm-opt-o2',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-clang',
          'cflags' : ('-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -O2 --sysroot=' +
                      os.path.abspath(os.path.join(
                          os.path.dirname(__file__),
                          os.pardir,
                          'install-llvm-arm/arm-none-eabi'))),
          'ldflags' : '-fuse-ld=bfd',
          'path' : 'install-llvm-arm',
        },
        { 'name' : 'fosdem-arm-llvm-opt-o3',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-clang',
          'cflags' : ('-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -O3 --sysroot=' +
                      os.path.abspath(os.path.join(
                          os.path.dirname(__file__),
                          os.pardir,
                          'install-llvm-arm/arm-none-eabi'))),
          'ldflags' : '-fuse-ld=bfd',
          'path' : 'install-llvm-arm',
        },
    ]
}

rv32_gcc_opt_runset = {
    'name' : 'RV32IMC GCC optimization comparison',
    'size benchmark' : {
        'timeout' : 30,
        'arglist' : [
            './benchmark_size.py',
            '--json-output',
        ],
        'desc' : 'sized'
    },
    'speed benchmark' : {
        'timeout' : 1800,
        'arglist' : [
            './benchmark_speed.py',
            '--target-module=run_gdbserver_sim',
	    '--gdbserver-command=riscv32-gdbserver',
	    '--gdb-command=riscv32-unknown-elf-gdb',
            '--json-output',
        ],
        'desc' : 'run'
    },
    'runs' : [
        { 'name' : 'rv32imc-opt-lto-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore -flto',
          'ldflags' : '-flto',
          'path' : 'install-rv32-gcc-10.0.0',
          'env' : ('AR=riscv32-unknown-elf-gcc-ar,' +
                   'RANLIB=riscv32-unknown-elf-gcc-ranlib')
        },
        { 'name' : 'rv32imc-opt-lto-o3',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O3 -flto',
          'ldflags' : '-flto',
          'path' : 'install-rv32-gcc-10.0.0',
          'env' : ('AR=riscv32-unknown-elf-gcc-ar,' +
                   'RANLIB=riscv32-unknown-elf-gcc-ranlib')
        },
        { 'name' : 'rv32imc-opt-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'ldflags' : '',
          'path' : 'install-rv32-gcc-10.0.0',
        },
        { 'name' : 'rv32imc-opt-os',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os',
          'ldflags' : '',
          'path' : 'install-rv32-gcc-10.0.0',
        },
        { 'name' : 'rv32imc-opt-o0',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O0',
          'ldflags' : '',
          'path' : 'install-rv32-gcc-10.0.0',
        },
        { 'name' : 'rv32imc-opt-o1',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O1',
          'ldflags' : '',
          'path' : 'install-rv32-gcc-10.0.0',
        },
        { 'name' : 'rv32imc-opt-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'ldflags' : '',
          'path' : 'install-rv32-gcc-10.0.0',
        },
        { 'name' : 'rv32imc-opt-o3',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O3',
          'ldflags' : '',
          'path' : 'install-rv32-gcc-10.0.0',
        },
        { 'name' : 'rv32imc-opt-o3-inline-40',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O3 -finline-functions ' +
                     '-finline-limit=40',
          'ldflags' : '',
          'path' : 'install-rv32-gcc-10.0.0',
        },
        { 'name' : 'rv32imc-opt-o3-unroll-inline-200',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O3 -funroll-all-loops ' +
                     '-finline-functions -finline-limit=200',
          'ldflags' : '',
          'path' : 'install-rv32-gcc-10.0.0',
        },
    ]
}

rv32_llvm_opt_runset = {
    'name' : 'RV32IMC LLVM optimization comparison',
    'size benchmark' : {
        'timeout' : 30,
        'arglist' : [
            './benchmark_size.py',
            '--json-output',
        ],
        'desc' : 'sized'
    },
    'speed benchmark' : {
        'timeout' : 1800,
        'arglist' : [
            './benchmark_speed.py',
            '--target-module=run_gdbserver_sim',
	    '--gdbserver-command=riscv32-gdbserver',
	    '--gdb-command=riscv32-unknown-elf-gdb',
            '--json-output',
        ],
        'desc' : 'run'
    },
    'runs' : [
        { 'name' : 'rv32imc-llvm-opt-oz-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-clang',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Oz -msave-restore',
          'ldflags' : '',
          'path' : 'install-riscv32-llvm-ljr',
        },
    ]
}

rv32_gcc_isa_runset = {
    'name' : 'RV32 GCC ISA comparison',
    'size benchmark' : {
        'timeout' : 30,
        'arglist' : [
            './benchmark_size.py',
            '--json-output',
        ],
        'desc' : 'sized'
    },
    'speed benchmark' : {
        'timeout' : 1800,
        'arglist' : [
            './benchmark_speed.py',
            '--target-module=run_gdbserver_sim',
	    '--gdbserver-command=riscv32-gdbserver',
	    '--gdb-command=riscv32-unknown-elf-gdb',
            '--json-output',
        ],
        'desc' : 'run'
    },
    'runs' : [
        { 'name' : 'rv32e-isa-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32e -mabi=ilp32e -Os -msave-restore',
          'ldflags' : '',
        },
        { 'name' : 'rv32ec-isa-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32ec -mabi=ilp32e -Os -msave-restore',
          'ldflags' : '',
        },
        { 'name' : 'rv32i-isa-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32i -mabi=ilp32 -Os -msave-restore',
          'ldflags' : '',
        },
        { 'name' : 'rv32ic-isa-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32ic -mabi=ilp32 -Os -msave-restore',
          'ldflags' : '',
        },
        { 'name' : 'rv32im-isa-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32im -mabi=ilp32 -Os -msave-restore',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-isa-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'ldflags' : '',
        },
        { 'name' : 'rv32e-isa-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32e -mabi=ilp32e -O2',
          'ldflags' : '',
        },
        { 'name' : 'rv32ec-isa-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32ec -mabi=ilp32e -O2',
          'ldflags' : '',
        },
        { 'name' : 'rv32i-isa-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32i -mabi=ilp32 -O2',
          'ldflags' : '',
        },
        { 'name' : 'rv32ic-isa-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32ic -mabi=ilp32 -O2',
          'ldflags' : '',
        },
        { 'name' : 'rv32im-isa-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32im -mabi=ilp32 -O2',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-isa-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'ldflags' : '',
        },
    ]
}


rv32_gcc_version_runset = {
    'name' : 'RV32 GCC compiler version comparison',
    'size benchmark' : {
        'timeout' : 30,
        'arglist' : [
            './benchmark_size.py',
            '--json-output',
        ],
        'desc' : 'sized'
    },
    'speed benchmark' : {
        'timeout' : 1800,
        'arglist' : [
            './benchmark_speed.py',
            '--target-module=run_gdbserver_sim',
	    '--gdbserver-command=riscv32-gdbserver',
	    '--gdb-command=riscv32-unknown-elf-gdb',
            '--json-output',
        ],
        'desc' : 'run'
    },
    'runs' : [
        { 'name' : 'rv32imc-version-7-1-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'path' : 'install-rv32-gcc_7.1',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-7-2-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'path' : 'install-rv32-gcc_7.2',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-7-3-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'path' : 'install-rv32-gcc_7.3',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-7-4-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'path' : 'install-rv32-gcc_7.4',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-7-5-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'path' : 'install-rv32-gcc_7.5',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-8-1-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'path' : 'install-rv32-gcc_8.1',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-8-2-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'path' : 'install-rv32-gcc_8.2',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-8-3-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'path' : 'install-rv32-gcc_8.3',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-9-1-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'path' : 'install-rv32-gcc_9.1',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-9-2-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'path' : 'install-rv32-gcc_9.2',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-master-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'path' : 'install-rv32-gcc_10.0.0',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-7-1-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'path' : 'install-rv32-gcc_7.1',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-7-2-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'path' : 'install-rv32-gcc_7.2',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-7-3-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'path' : 'install-rv32-gcc_7.3',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-7-4-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'path' : 'install-rv32-gcc_7.4',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-7-5-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'path' : 'install-rv32-gcc_7.5',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-8-1-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'path' : 'install-rv32-gcc_8.1',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-8-2-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'path' : 'install-rv32-gcc_8.2',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-8-3-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'path' : 'install-rv32-gcc_8.3',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-9-1-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'path' : 'install-rv32-gcc_9.1',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-9-2-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'path' : 'install-rv32-gcc_9.2',
          'ldflags' : '',
        },
        { 'name' : 'rv32imc-version-master-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'path' : 'install-rv32-gcc_10.0.0',
          'ldflags' : '',
        },
    ]
}

gcc_arch_runset = {
    'name' : 'RV32IMC GCC optimization comparison',
    'size benchmark' : {
        'timeout' : 30,
        'arglist' : [
            './benchmark_size.py',
            '--json-output',
        ],
        'desc' : 'sized'
    },
    'runs' : [
        { 'name' : 'arc-arch-os',
          'arch' : 'arc',
          'chip' : 'em',
	  'board' : 'generic',
          'cc' : 'arc-elf32-gcc',
          'cflags' : '-mcpu=em -Os',
          'ldflags' : '',
          'path' : 'install-arc-gcc-10.0.0',
        },
        { 'name' : 'arm-arch-os',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -Os',
          'ldflags' : '',
          'path' : 'install-arm-gcc-10.0.0',
        },
        { 'name' : 'avr-arch-os',
          'arch' : 'avr',
          'chip' : 'atmega64',
	  'board' : 'generic',
          'cc' : 'avr-gcc',
          'cflags' : '-mmcu=avr5 -Os',
          'ldflags' : '-mmcu=avr5 -Wl,-no-gc-sections',
          'path' : 'install-avr-gcc-10.0.0',
        },
        { 'name' : 'rv32imc-arch-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'ldflags' : '',
          'path' : 'install-rv32-gcc_10.0.0',
        },
        { 'name' : 'arc-arch-o2',
          'arch' : 'arc',
          'chip' : 'em',
	  'board' : 'generic',
          'cc' : 'arc-elf32-gcc',
          'cflags' : '-mcpu=em -O2',
          'ldflags' : '',
          'path' : 'install-arc-gcc-10.0.0',
        },
        { 'name' : 'arm-arch-o2',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -O2',
          'ldflags' : '',
          'path' : 'install-arm-gcc-10.0.0',
        },
        { 'name' : 'avr-arch-o2',
          'arch' : 'avr',
          'chip' : 'atmega64',
	  'board' : 'generic',
          'cc' : 'avr-gcc',
          'cflags' : '-mmcu=avr5 -O2',
          'ldflags' : '-mmcu=avr5 -Wl,-no-gc-sections',
          'path' : 'install-avr-gcc-10.0.0',
        },
        { 'name' : 'rv32imc-arch-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'ldflags' : '',
          'path' : 'install-rv32-gcc_10.0.0',
        },
    ]
}

gcc9_arch_runset = {
    'name' : 'RV32IMC GCC optimization comparison',
    'size benchmark' : {
        'timeout' : 30,
        'arglist' : [
            './benchmark_size.py',
            '--json-output',
        ],
        'desc' : 'sized'
    },
    'runs' : [
        { 'name' : 'arc-arch-gcc-9.2-os',
          'arch' : 'arc',
          'chip' : 'em',
	  'board' : 'generic',
          'cc' : 'arc-elf32-gcc',
          'cflags' : '-mcpu=em -Os',
          'ldflags' : '',
          'path' : 'install-arc-gcc-9.2',
        },
        { 'name' : 'arm-arch-gcc-9.2-os',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -Os',
          'ldflags' : '',
          'path' : 'install-arm-gcc-9.2',
        },
        { 'name' : 'avr-arch-gcc-9.2-os',
          'arch' : 'avr',
          'chip' : 'atmega64',
	  'board' : 'generic',
          'cc' : 'avr-gcc',
          'cflags' : '-mmcu=avr5 -Os',
          'ldflags' : '-mmcu=avr5',
          'path' : 'install-avr-gcc-9.2',
        },
        { 'name' : 'rv32imc-arch-gcc-9.2-os-save-restore',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
          'ldflags' : '',
          'path' : 'install-rv32-gcc_9.2',
        },
        { 'name' : 'arc-arch-gcc-9.2-o2',
          'arch' : 'arc',
          'chip' : 'em',
	  'board' : 'generic',
          'cc' : 'arc-elf32-gcc',
          'cflags' : '-mcpu=em -O2',
          'ldflags' : '',
          'path' : 'install-arc-gcc-9.2',
        },
        { 'name' : 'arm-arch-gcc-9.2-o2',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -O2',
          'ldflags' : '',
          'path' : 'install-arm-gcc-9.2',
        },
        { 'name' : 'avr-arch-gcc-9.2-o2',
          'arch' : 'avr',
          'chip' : 'atmega64',
	  'board' : 'generic',
          'cc' : 'avr-gcc',
          'cflags' : '-mmcu=avr5 -O2',
          'ldflags' : '-mmcu=avr5',
          'path' : 'install-avr-gcc-9.2',
        },
        { 'name' : 'rv32imc-arch-gcc-9.2-o2',
          'arch' : 'riscv32',
          'chip' : 'generic',
	  'board' : 'ri5cyverilator',
          'cc' : 'riscv32-unknown-elf-gcc',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
          'ldflags' : '',
          'path' : 'install-rv32-gcc_9.2',
        },
    ]
}


arm_gcc_version_runset = {
    'name' : 'Arm Cortex M4 compiler version comparison',
    'size benchmark' : {
        'timeout' : 30,
        'arglist' : [
            './benchmark_size.py',
            '--json-output',
        ],
        'desc' : 'sized'
    },
    'runs' : [
        { 'name' : 'arm-version-4.9.4-os-thumb2',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -std=c11 -Os',
          'ldflags' : '',
          'path' : 'install-arm-gcc-4.9.4',
        },
        { 'name' : 'arm-version-5-5-os-thumb2',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -std=c11 -Os',
          'ldflags' : '',
          'path' : 'install-arm-gcc-5.5',
        },
        { 'name' : 'arm-version-6-5-os-thumb2',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -std=c11 -Os',
          'ldflags' : '',
          'path' : 'install-arm-gcc-6.5',
        },
        { 'name' : 'arm-version-7-5-os-thumb2',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -std=c11 -Os',
          'ldflags' : '',
          'path' : 'install-arm-gcc-7.5',
        },
        { 'name' : 'arm-version-8-3-os-thumb2',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -std=c11 -Os',
          'ldflags' : '',
          'path' : 'install-arm-gcc-8.3',
        },
        { 'name' : 'arm-version-9-2-os-thumb2',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -std=c11 -Os',
          'ldflags' : '',
          'path' : 'install-arm-gcc-9.2',
        },
        { 'name' : 'arm-version-master-os-thumb2',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -std=c11 -Os',
          'ldflags' : '',
          'path' : 'install-arm-gcc-10.0.0',
        },
    ]
}


def build_parser():
    """Build a parser for all the arguments"""
    parser = argparse.ArgumentParser(description='Build all the benchmarks')

    parser.add_argument(
        '--benchmark',
        type=str,
        default=[],
        nargs='+',
        help='Benchmark name(s) to build. By default all tests are build.'
    )
    parser.add_argument(
        '--exclude',
        type=str,
        default=[],
        nargs='+',
        help='Benchmark name(s) to exclude.'
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='More messages'
    )
    parser.add_argument(
        '--builddir',
        default='bd',
        help='Directory in which to build benchmarks and support code',
    )
    parser.add_argument(
        '--logdir',
        default='logs',
        help='Directory in which to store logs',
    )
    parser.add_argument(
        '--resdir',
        type=str,
        default='results',
        help='Directory in which to place results files',
    )
    parser.add_argument(
        '--fosdem-rv32-gcc-opt',
        action='store_true',
        help='Run FOSDEM RV32IMC GCC optimization comparison benchmarks'
    )
    parser.add_argument(
        '--fosdem-rv32-llvm-opt',
        action='store_true',
        help='Run FOSDEM RV32IMC Clang/LLVM optimization comparison benchmarks'
    )
    parser.add_argument(
        '--fosdem-arm-gcc-opt',
        action='store_true',
        help='Run FOSDEM Arm Cortex M4 GCC optimization comparison benchmarks'
    )
    parser.add_argument(
        '--fosdem-arm-llvm-opt',
        action='store_true',
        help='Run FOSDEM Arm Cortex M4 Clang/LLVM optimization comparison benchmarks'
    )
    parser.add_argument(
        '--rv32-gcc-opt',
        action='store_true',
        help='Run RISC-V GCC optimization comparison benchmarks'
    )
    parser.add_argument(
        '--rv32-llvm-opt',
        action='store_true',
        help='Run RISC-V Clang/LLVM optimization comparison benchmarks'
    )
    parser.add_argument(
        '--rv32-gcc-isa',
        action='store_true',
        help='Run RISC-V GCC isa comparison benchmarks'
    )
    parser.add_argument(
        '--rv32-gcc-version',
        action='store_true',
        help='Run RISC-V GCC version comparison benchmarks'
    )
    parser.add_argument(
        '--gcc-arch',
        action='store_true',
        help='Run GCC architecture comparison benchmarks'
    )
    parser.add_argument(
        '--gcc9-arch',
        action='store_true',
        help='Run GCC 9.2 architecture comparison benchmarks'
    )
    parser.add_argument(
        '--arm-gcc-version',
        action='store_true',
        help='Run Arm GCC version comparison benchmarks'
    )

    return parser


def build_benchmarks(benchmark, exclude, builddir, logdir, arch, chip, board, cc=None, cflags=None, ldflags=None,
                     dummy_libs=None, user_libs=None, env=None,
                     ld=None, cpu_mhz=None, warmup_heat=None, verbose=False):
    """Build all the benchmarks"""

    # Construct the argument list
    arglist = [
        f'./build_all.py',
        f'--clean',
        f'--verbose',
        f'--builddir={builddir}',
        f'--logdir={logdir}',
        f'--arch={arch}',
        f'--chip={chip}',
	f'--board={board}',
    ]
    if cc:
        arglist.append(f'--cc={cc}')
    if ld:
        arglist.append(f'--ld={ld}')
    if cflags:
        arglist.append(f'--cflags={cflags}')
    if ldflags:
        arglist.append(f'--ldflags={ldflags}')
    if dummy_libs:
        arglist.append(f'--dummy-libs={dummy_libs}')
    if user_libs:
        arglist.append(f'--user-libs={user_libs}')
    if env:
        arglist.append(f'--env={env}')
    if cpu_mhz:
        arglist.append(f'--cpu-mhz={cpu_mhz}')
    if warmup_heat:
        arglist.append(f'--warmup-heat={warmup_heat}')
    if benchmark:
        arglist += ['--benchmark'] + benchmark
    if exclude:
        arglist += ['--exclude'] + exclude

    # Run the build script
    if verbose:
        print(arglist_to_str(arglist))
    try:
        res = subprocess.run(
            arglist,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            timeout=30,
        )
        if res.returncode != 0:
            print(res.stdout.decode('utf-8'))
            print(f'ERROR: {arglist_to_str(arglist)} failed')
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print(res.stdout.decode('utf-8'))
        print(f'ERROR: {arglist_to_str(arglist)} timed out')
        sys.exit(1)


def benchmark(arglist, timeout, desc, resfile, append, verbose=False):
    """Run the speed benchmark script"""

    # Run the benchmark script
    succeeded = True
    if verbose:
        print(arglist_to_str(arglist))
    try:
        res = subprocess.run(
            arglist,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        if res.returncode != 0:
            print(res.stdout.decode('utf-8'))
            print(f'ERROR: {arglist_to_str(arglist)} failed')
            succeeded = False
    except subprocess.TimeoutExpired:
        print(res.stdout.decode('utf-8'))
        print(f'ERROR: {arglist_to_str(arglist)} timed out')
        succeeded = False

    # Dump the data if successful
    if succeeded:
        mode = 'a' if append else 'w'
        with open(resfile, mode) as fileh:
            for line in res.stdout.decode('utf-8').splitlines(keepends=True):
                if not 'All benchmarks ' + desc + ' successfully' in line:
                    fileh.writelines(line)
            fileh.close()


def prepend_path(path):
    install_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        path,
        'bin'
    ))
    env = os.environ
    old_path = env['PATH']
    env['PATH'] = install_dir + os.pathsep + env['PATH']
    return env, old_path


# a list of scalar parameters
scalar_params = (
    'name', 'arch', 'chip', 'board', 'cc', 'ld', 'cpu_mhz', 'warmup_heat',
    'nostartfiles', 'nostdlib',
)
# a list of list parameters. value: separator
#   `dummy-libs` is not included.  It is set to a fixed value on the size benchmark.
list_params = {
    'cflags': ' ', 'ldflags': ' ', 'user_libs': ',', 'path': ':', 'env': ':',
}


def check_params(params):
    for key in params:
        if not (key in list_params) and not (key in scalar_params):
            print(f"Warning: Unknown parameter {key}. Ignored.")


def merge_params(orig, add):
    dest = orig.copy()
    for key in add:
        if key in list_params:
            if key in dest:
                dest[key] += list_params[key] + add[key]
            else:
                dest[key] = add[key]
        elif key in scalar_params:
            dest[key] = add[key]
        else:
            print(f"Warning: Unknown parameter {key}. Ignored.")
    return dest


def main():
    """Main program to drive building of benchmarks."""

    # Parse arguments using standard technology
    parser = build_parser()
    args = parser.parse_args()

    runsets = []

    if args.fosdem_rv32_gcc_opt:
        runsets.append(fosdem_rv32_gcc_opt_runset)
    if args.fosdem_rv32_llvm_opt:
        runsets.append(fosdem_rv32_llvm_opt_runset)
    if args.fosdem_arm_gcc_opt:
        runsets.append(fosdem_arm_gcc_opt_runset)
    if args.fosdem_arm_llvm_opt:
        runsets.append(fosdem_arm_llvm_opt_runset)
    if args.rv32_gcc_opt:
        runsets.append(rv32_gcc_opt_runset)
    if args.rv32_llvm_opt:
        runsets.append(rv32_llvm_opt_runset)
    if args.rv32_gcc_isa:
        runsets.append(rv32_gcc_isa_runset)
    if args.rv32_gcc_version:
        runsets.append(rv32_gcc_version_runset)
    if args.gcc_arch:
        runsets.append(gcc_arch_runset)
    if args.gcc9_arch:
        runsets.append(gcc9_arch_runset)
    if args.arm_gcc_version:
        runsets.append(arm_gcc_version_runset)

    if not runsets:
        print("ERROR: No run sets specified")
        sys.exit(1)

    # Take each runset in turn
    for rs in runsets:
        print(rs['name'])
        if 'common' in rs:
            check_params(rs['common'])

        for r in rs['runs']:
            if 'common' in rs:
                r = merge_params(rs['common'], r)

            name = r['name']
            if 'nostartfiles' in r:
                nostartfiles = r['nostartfiles']
            else:
                nostartfiles = '-nostartfiles'
            if 'nostdlib' in r:
                nostdlib = r['nostdlib']
            else:
                nostdlib = '-nostdlib'
            if r['ldflags']:
                ldflags_size = r['ldflags'] + f' {nostartfiles} {nostdlib}'
            else:
                ldflags_size = f'{nostartfiles} {nostdlib}'

            if 'user_libs' in r:
                user_libs_speed = r['user_libs']
            else:
                user_libs_speed = '-lm'

            print(f'  {name}')
            resfile = os.path.join(args.resdir, name + '.json')
            if not os.path.isdir(args.resdir):
                try:
                    os.makedirs(args.resdir)
                except PermissionError:
                    log.error(f'ERROR: Unable to create build directory {args.resdir}: exiting')
                    sys.exit(1)

            add_arglist = [f'--builddir={args.builddir}', f'--logdir={args.logdir}']
            if args.benchmark:
                add_arglist += ['--benchmark'] + args.benchmark
            if args.exclude:
                add_arglist += ['--exclude'] + args.exclude
            if args.verbose:
                add_arglist += ['--verbose']

            path = r.get('path')
            if path:
                env, oldpath = prepend_path(path)
            else:
                env = None

            # Size benchmark
            if 'size benchmark' in rs:
                build_benchmarks(
                    benchmark=args.benchmark,
                    exclude=args.exclude,
                    builddir=args.builddir,
                    logdir=args.logdir,
                    arch=r['arch'],
                    chip=r['chip'],
                    board=r['board'],
                    cc=r.get('cc'),
                    ld=r.get('ld'),
                    cflags=r.get('cflags'),
                    ldflags=ldflags_size,
                    dummy_libs='crt0 libc libgcc libm',
                    env=r.get('env'),
                    cpu_mhz=r.get('cpu_mhz'),
                    warmup_heat=r.get('warmup_heat'),
                    verbose=args.verbose,
                )
                add_arglist_size = ['--json-comma'] if 'speed benchmark' in rs else []
                benchmark(
                    arglist=rs['size benchmark']['arglist'] + add_arglist + add_arglist_size,
                    timeout=rs['size benchmark']['timeout'],
                    desc=rs['size benchmark']['desc'],
                    resfile=resfile,
                    append=False,
                    verbose=args.verbose,
                )

            # Speed benchmark
            if 'speed benchmark' in rs:
                build_benchmarks(
                    benchmark=args.benchmark,
                    exclude=args.exclude,
                    builddir=args.builddir,
                    logdir=args.logdir,
                    arch=r['arch'],
                    chip=r['chip'],
                    board=r['board'],
                    cc=r.get('cc'),
                    ld=r.get('ld'),
                    cflags=r.get('cflags'),
                    ldflags=r.get('ldflags'),
                    user_libs=user_libs_speed,
                    env=r.get('env'),
                    cpu_mhz=r.get('cpu_mhz'),
                    warmup_heat=r.get('warmup_heat'),
                    verbose=args.verbose,
                )
                add_arglist_speed = ['--no-json-head'] if 'size benchmark' in rs else []
                if 'timeout' in rs['speed benchmark']:
                    timeout = rs['speed benchmark']['timeout']
                    add_arglist_speed += [f'--timeout={timeout}']
                benchmark(
                    arglist=rs['speed benchmark']['arglist'] + add_arglist + add_arglist_speed,
                    timeout=rs['speed benchmark']['timeout'],
                    desc=rs['speed benchmark']['desc'],
                    resfile=resfile,
                    append=True,
                    verbose=args.verbose,
                )

            # Restore the environment
            if path:
                env['PATH'] = oldpath

# Make sure we have new enough Python and only run if this is the main package

check_python_version(3, 6)
if __name__ == '__main__':
    sys.exit(main())
