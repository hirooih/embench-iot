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


import sys
import os
from run_all import build_parser, run_all


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
    'common' : {
        'arch' : 'riscv32',
        'chip' : 'generic',
        'board' : 'ri5cyverilator',
        'cc' : 'riscv32-unknown-elf-gcc',
        'cflags' : '-march=rv32imc -mabi=ilp32',
        'path' : 'install-gcc',
    },
    'runs' : [
        { 'name' : 'fosdem-rv32-gcc-opt-o0',
          'cflags' : '-O0',
        },
        { 'name' : 'fosdem-rv32-gcc-opt-os-save-restore',
          'cflags' : '-Os -msave-restore',
        },
        { 'name' : 'fosdem-rv32-gcc-opt-og',
          'cflags' : '-Og',
        },
        { 'name' : 'fosdem-rv32-gcc-opt-o1',
          'cflags' : '-O1',
        },
        { 'name' : 'fosdem-rv32-gcc-opt-o2',
          'cflags' : '-O2',
        },
        { 'name' : 'fosdem-rv32-gcc-opt-o3',
          'cflags' : '-O3',
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
    'common' : {
        'arch' : 'riscv32',
        'chip' : 'generic',
        'board' : 'ri5cyverilator',
        'cc' : 'riscv32-unknown-elf-clang',
        'cflags' : '-march=rv32imc -mabi=ilp32',
        'path' : 'install-llvm',
    },
    'runs' : [
        { 'name' : 'fosdem-rv32-llvm-opt-o0',
          'cflags' : '-O0',
        },
        { 'name' : 'fosdem-rv32-llvm-opt-os-save-restore',
          'cflags' : '-Os -msave-restore',
        },
        { 'name' : 'fosdem-rv32-llvm-opt-oz-save-restore',
          'cflags' : '-Oz -msave-restore',
        },
        { 'name' : 'fosdem-rv32-llvm-opt-o1',
          'cflags' : '-O1',
        },
        { 'name' : 'fosdem-rv32-llvm-opt-o2',
          'cflags' : '-O2',
        },
        { 'name' : 'fosdem-rv32-llvm-opt-o3',
          'cflags' : '-O3',
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
    'common' : {
        'arch' : 'arm',
        'chip' : 'cortex-m4',
        'board' : 'generic',
        'cc' : 'arm-none-eabi-gcc',
        'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft',
        'path' : 'install-gcc-arm',
    },
    'runs' : [
        { 'name' : 'fosdem-arm-gcc-opt-o0',
          'cflags' : '-O0',
        },
        { 'name' : 'fosdem-arm-gcc-opt-os',
          'cflags' : '-Os',
        },
        { 'name' : 'fosdem-arm-gcc-opt-og',
          'cflags' : '-Og',
        },
        { 'name' : 'fosdem-arm-gcc-opt-o1',
          'cflags' : '-O1',
        },
        { 'name' : 'fosdem-arm-gcc-opt-o2',
          'cflags' : '-O2',
        },
        { 'name' : 'fosdem-arm-gcc-opt-o3',
          'cflags' : '-O3',
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
    'common' : {
        'arch' : 'arm',
        'chip' : 'cortex-m4',
        'board' : 'generic',
        'cc' : 'arm-none-eabi-clang',
        'cflags' : ('-mcpu=cortex-m4 -mthumb -mfloat-abi=soft --sysroot=' +
                    os.path.abspath(os.path.join(
                        os.path.dirname(__file__),
                        os.pardir,
                        'install-llvm-arm/arm-none-eabi'))),
        'ldflags' : '-fuse-ld=bfd',
        'path' : 'install-llvm-arm',
    },
    'runs' : [
        { 'name' : 'fosdem-arm-llvm-opt-o0',
          'cflags' : '-O0',
        },
        { 'name' : 'fosdem-arm-llvm-opt-os',
          'cflags' : '-Os',
        },
        { 'name' : 'fosdem-arm-llvm-opt-oz',
          'cflags' : '-Oz',
        },
        { 'name' : 'fosdem-arm-llvm-opt-o1',
          'cflags' : '-O1',
        },
        { 'name' : 'fosdem-arm-llvm-opt-o2',
          'cflags' : '-O2',
        },
        { 'name' : 'fosdem-arm-llvm-opt-o3',
          'cflags' : '-O3',
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
    'common' : {
        'arch' : 'riscv32',
        'chip' : 'generic',
        'board' : 'ri5cyverilator',
        'cc' : 'riscv32-unknown-elf-gcc',
        'cflags' : '-march=rv32imc -mabi=ilp32',
        'path' : 'install-rv32-gcc-10.0.0',
    },
    'runs' : [
        { 'name' : 'rv32imc-opt-lto-os-save-restore',
          'cflags' : '-Os -msave-restore -flto',
          'ldflags' : '-flto',
          'env' : ('AR=riscv32-unknown-elf-gcc-ar,' +
                   'RANLIB=riscv32-unknown-elf-gcc-ranlib')
        },
        { 'name' : 'rv32imc-opt-lto-o3',
          'cflags' : '-O3 -flto',
          'ldflags' : '-flto',
          'env' : ('AR=riscv32-unknown-elf-gcc-ar,' +
                   'RANLIB=riscv32-unknown-elf-gcc-ranlib')
        },
        { 'name' : 'rv32imc-opt-os-save-restore',
          'cflags' : '-Os -msave-restore',
        },
        { 'name' : 'rv32imc-opt-os',
          'cflags' : '-Os',
        },
        { 'name' : 'rv32imc-opt-o0',
          'cflags' : '-O0',
        },
        { 'name' : 'rv32imc-opt-o1',
          'cflags' : '-O1',
        },
        { 'name' : 'rv32imc-opt-o2',
          'cflags' : '-O2',
        },
        { 'name' : 'rv32imc-opt-o3',
          'cflags' : '-O3',
        },
        { 'name' : 'rv32imc-opt-o3-inline-40',
          'cflags' : '-O3 -finline-functions -finline-limit=40',
        },
        { 'name' : 'rv32imc-opt-o3-unroll-inline-200',
          'cflags' : '-O3 -funroll-all-loops -finline-functions -finline-limit=200',
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
    'common' : {
        'arch' : 'riscv32',
        'chip' : 'generic',
        'board' : 'ri5cyverilator',
        'cc' : 'riscv32-unknown-elf-gcc',
    },
    'runs' : [
        { 'name' : 'rv32e-isa-os-save-restore',
          'cflags' : '-march=rv32e -mabi=ilp32e -Os -msave-restore',
        },
        { 'name' : 'rv32ec-isa-os-save-restore',
          'cflags' : '-march=rv32ec -mabi=ilp32e -Os -msave-restore',
        },
        { 'name' : 'rv32i-isa-os-save-restore',
          'cflags' : '-march=rv32i -mabi=ilp32 -Os -msave-restore',
        },
        { 'name' : 'rv32ic-isa-os-save-restore',
          'cflags' : '-march=rv32ic -mabi=ilp32 -Os -msave-restore',
        },
        { 'name' : 'rv32im-isa-os-save-restore',
          'cflags' : '-march=rv32im -mabi=ilp32 -Os -msave-restore',
        },
        { 'name' : 'rv32imc-isa-os-save-restore',
          'cflags' : '-march=rv32imc -mabi=ilp32 -Os -msave-restore',
        },
        { 'name' : 'rv32e-isa-o2',
          'cflags' : '-march=rv32e -mabi=ilp32e -O2',
        },
        { 'name' : 'rv32ec-isa-o2',
          'cflags' : '-march=rv32ec -mabi=ilp32e -O2',
        },
        { 'name' : 'rv32i-isa-o2',
          'cflags' : '-march=rv32i -mabi=ilp32 -O2',
        },
        { 'name' : 'rv32ic-isa-o2',
          'cflags' : '-march=rv32ic -mabi=ilp32 -O2',
        },
        { 'name' : 'rv32im-isa-o2',
          'cflags' : '-march=rv32im -mabi=ilp32 -O2',
        },
        { 'name' : 'rv32imc-isa-o2',
          'cflags' : '-march=rv32imc -mabi=ilp32 -O2',
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
    'common' : {
        'arch' : 'riscv32',
        'chip' : 'generic',
        'board' : 'ri5cyverilator',
        'cc' : 'riscv32-unknown-elf-gcc',
        'cflags' : '-march=rv32imc -mabi=ilp32',
    },
    'runs' : [
        { 'name' : 'rv32imc-version-7-1-os-save-restore',
          'cflags' : '-Os -msave-restore',
          'path' : 'install-rv32-gcc_7.1',
        },
        { 'name' : 'rv32imc-version-7-2-os-save-restore',
          'cflags' : '-Os -msave-restore',
          'path' : 'install-rv32-gcc_7.2',
        },
        { 'name' : 'rv32imc-version-7-3-os-save-restore',
          'cflags' : '-Os -msave-restore',
          'path' : 'install-rv32-gcc_7.3',
        },
        { 'name' : 'rv32imc-version-7-4-os-save-restore',
          'cflags' : '-Os -msave-restore',
          'path' : 'install-rv32-gcc_7.4',
        },
        { 'name' : 'rv32imc-version-7-5-os-save-restore',
          'cflags' : '-Os -msave-restore',
          'path' : 'install-rv32-gcc_7.5',
        },
        { 'name' : 'rv32imc-version-8-1-os-save-restore',
          'cflags' : '-Os -msave-restore',
          'path' : 'install-rv32-gcc_8.1',
        },
        { 'name' : 'rv32imc-version-8-2-os-save-restore',
          'cflags' : '-Os -msave-restore',
          'path' : 'install-rv32-gcc_8.2',
        },
        { 'name' : 'rv32imc-version-8-3-os-save-restore',
          'cflags' : '-Os -msave-restore',
          'path' : 'install-rv32-gcc_8.3',
        },
        { 'name' : 'rv32imc-version-9-1-os-save-restore',
          'cflags' : '-Os -msave-restore',
          'path' : 'install-rv32-gcc_9.1',
        },
        { 'name' : 'rv32imc-version-9-2-os-save-restore',
          'cflags' : '-Os -msave-restore',
          'path' : 'install-rv32-gcc_9.2',
        },
        { 'name' : 'rv32imc-version-master-os-save-restore',
          'cflags' : '-Os -msave-restore',
          'path' : 'install-rv32-gcc_10.0.0',
        },
        { 'name' : 'rv32imc-version-7-1-o2',
          'cflags' : '-O2',
          'path' : 'install-rv32-gcc_7.1',
        },
        { 'name' : 'rv32imc-version-7-2-o2',
          'cflags' : '-O2',
          'path' : 'install-rv32-gcc_7.2',
        },
        { 'name' : 'rv32imc-version-7-3-o2',
          'cflags' : '-O2',
          'path' : 'install-rv32-gcc_7.3',
        },
        { 'name' : 'rv32imc-version-7-4-o2',
          'cflags' : '-O2',
          'path' : 'install-rv32-gcc_7.4',
        },
        { 'name' : 'rv32imc-version-7-5-o2',
          'cflags' : '-O2',
          'path' : 'install-rv32-gcc_7.5',
        },
        { 'name' : 'rv32imc-version-8-1-o2',
          'cflags' : '-O2',
          'path' : 'install-rv32-gcc_8.1',
        },
        { 'name' : 'rv32imc-version-8-2-o2',
          'cflags' : '-O2',
          'path' : 'install-rv32-gcc_8.2',
        },
        { 'name' : 'rv32imc-version-8-3-o2',
          'cflags' : '-O2',
          'path' : 'install-rv32-gcc_8.3',
        },
        { 'name' : 'rv32imc-version-9-1-o2',
          'cflags' : '-O2',
          'path' : 'install-rv32-gcc_9.1',
        },
        { 'name' : 'rv32imc-version-9-2-o2',
          'cflags' : '-O2',
          'path' : 'install-rv32-gcc_9.2',
        },
        { 'name' : 'rv32imc-version-master-o2',
          'cflags' : '-O2',
          'path' : 'install-rv32-gcc_10.0.0',
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
          'path' : 'install-arc-gcc-10.0.0',
        },
        { 'name' : 'arm-arch-os',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -Os',
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
          'path' : 'install-rv32-gcc_10.0.0',
        },
        { 'name' : 'arc-arch-o2',
          'arch' : 'arc',
          'chip' : 'em',
	  'board' : 'generic',
          'cc' : 'arc-elf32-gcc',
          'cflags' : '-mcpu=em -O2',
          'path' : 'install-arc-gcc-10.0.0',
        },
        { 'name' : 'arm-arch-o2',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -O2',
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
          'path' : 'install-arc-gcc-9.2',
        },
        { 'name' : 'arm-arch-gcc-9.2-os',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -Os',
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
          'path' : 'install-rv32-gcc_9.2',
        },
        { 'name' : 'arc-arch-gcc-9.2-o2',
          'arch' : 'arc',
          'chip' : 'em',
	  'board' : 'generic',
          'cc' : 'arc-elf32-gcc',
          'cflags' : '-mcpu=em -O2',
          'path' : 'install-arc-gcc-9.2',
        },
        { 'name' : 'arm-arch-gcc-9.2-o2',
          'arch' : 'arm',
          'chip' : 'cortex-m4',
	  'board' : 'generic',
          'cc' : 'arm-none-eabi-gcc',
          'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -O2',
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
    'common' : {
        'arch' : 'arm',
        'chip' : 'cortex-m4',
        'board' : 'generic',
        'cc' : 'arm-none-eabi-gcc',
        'cflags' : '-mcpu=cortex-m4 -mthumb -mfloat-abi=soft -std=c11',
    },
    'runs' : [
        { 'name' : 'arm-version-4.9.4-os-thumb2',
          'cflags' : '-Os',
          'path' : 'install-arm-gcc-4.9.4',
        },
        { 'name' : 'arm-version-5-5-os-thumb2',
          'cflags' : '-Os',
          'path' : 'install-arm-gcc-5.5',
        },
        { 'name' : 'arm-version-6-5-os-thumb2',
          'cflags' : '-Os',
          'path' : 'install-arm-gcc-6.5',
        },
        { 'name' : 'arm-version-7-5-os-thumb2',
          'cflags' : '-Os',
          'path' : 'install-arm-gcc-7.5',
        },
        { 'name' : 'arm-version-8-3-os-thumb2',
          'cflags' : '-Os',
          'path' : 'install-arm-gcc-8.3',
        },
        { 'name' : 'arm-version-9-2-os-thumb2',
          'cflags' : '-Os',
          'path' : 'install-arm-gcc-9.2',
        },
        { 'name' : 'arm-version-master-os-thumb2',
          'cflags' : '-Os',
          'path' : 'install-arm-gcc-10.0.0',
        },
    ]
}


def main():
    """Main program to drive building of benchmarks."""
    # Parse arguments using standard technology
    parser = build_parser()
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

    run_all(runsets, args)


if __name__ == '__main__':
    sys.exit(main())
