#!/usr/bin/env python3
# benchmark set for RV32 optimization comparison
# For speed benchmark, run_spike.py is used.

import sys
from run_all import build_parser, run_all

path = {
    "gcc": "/opt/riscv/bin",
    "clang": "/opt/riscv-trial/bin",
}
cc = {
    "gcc": "riscv64-unknown-elf-gcc",
    "clang": "clang",
}


def rv32_opt_runset(compiler, opt):
    cpre = compiler + '-'
    return {
        "name": "RV32IMC optimization comparison",
        "size benchmark": {
            "timeout": 30,
            "arglist": [
                "./benchmark_size.py",
                "--json-output",
                "--metric", "text", "rodata", "data",
            ],
            "desc": "sized",
        },
        "speed benchmark": {
            "timeout": 1800,
            "arglist": [
                "./benchmark_speed.py",
                "--json-output",
                "--target-module=run_spike",
                "--spike-command=/opt/riscv/bin/spike",
                "--spike-pk=/opt/riscv/riscv32-unknown-elf/bin/pk",
                # enable possible ISA extensions to be implemented
                '--spike-args=--isa=rv32im_zicsr_zicntr_zifencei_zba_zbb_zbc_zbs_zce_zicond',
            ],
            "desc": "run",
        },
        "common": {
            "arch": "riscv32",
            "chip": "generic",
            "board": "cycle",
            "path": path[compiler],
            "cc": cc[compiler],
            "cflags": "-v -c -mabi=ilp32 -ffunction-sections",
            "ldflags": "-march=rv32imc_zicsr -mabi=ilp32 -Wl,-gc-sections",
        },
        "runs": [
            {
                "name": f"{cpre}rv32im{opt}",
                "cflags": f"-march=rv32im_zicsr {opt}",
            },
            {
                "name": f"{cpre}rv32imc{opt}",
                "cflags": f"-march=rv32imc_zicsr {opt}",
            },
            {
                "name": f"{cpre}rv32imc_zcb{opt}",
                "cflags": f"-march=rv32imc_zicsr_zcb {opt}",
            },
            {
                "name": f"{cpre}rv32imbc_zcb{opt}",
                "cflags": f"-march=rv32imc_zicsr_zcb_zba_zbb_zbc_zbs {opt}",
            },
            {
                "name": f"{cpre}rv32imbc_zcb_zicond{opt}",
                "cflags": f"-march=rv32imc_zicsr_zcb_zba_zbb_zbc_zbs_zicond {opt}",
            },
            {
                "name": f"{cpre}rv32imbc_zcb_zicond{opt}-msave-restore",
                "cflags": f"-march=rv32imc_zicsr_zcb_zba_zbb_zbc_zbs_zicond {opt} -msave-restore",
            },
            {
                # Zcmp and Zcmt are not supported by binutils 2.44 yet
                "name": f"{cpre}rv32imbc_Zce_zicond{opt}",
                "cflags": f"-march=rv32imc_zicsr_zce_zba_zbb_zbc_zbs_zicond {opt}",
            },
            {
                # Zcmp and Zcmt are not supported by binutils 2.44 yet
                "name": f"{cpre}rv32imbc_Zce_zicond{opt}-msave-restore",
                "cflags": f"-march=rv32imc_zicsr_zce_zba_zbb_zbc_zbs_zicond {opt} -msave-restore",
            },
            # {
            #     "name": f"{cpre}rv32imbc_zcb_zicond{opt}-lto",
            #     "cflags": f"-march=rv32imc_zicsr_zcb_zba_zbb_zbc_zbs_zicond {opt} -flto",
            #     "ldflags": '-flto',
            # },
            # { 'name' : 'rv32imc-opt-O3-inline-40',
            #   'cflags' : '-O3 -finline-functions -finline-limit=40',
            # },
            # { 'name' : 'rv32imc-opt-O3-unroll-inline-200',
            #   'cflags' : '-O3 -funroll-all-loops -finline-functions -finline-limit=200',
            # },
        ],
    }


gcc_Os_runset = rv32_opt_runset('gcc', '-Os')
clang_Os_runset = rv32_opt_runset('clang', '-Os')
clang_Oz_runset = rv32_opt_runset('clang', '-Oz')


def main():
    """Main program to drive building of benchmarks."""
    # Parse arguments using standard technology
    parser = build_parser()

    parser.add_argument(
        "--gcc_Os_runset", action="store_true", help="Run gcc -Os option comparison"
    )
    parser.add_argument(
        "--clang_Os_runset", action="store_true", help="Run clang -Os option comparison"
    )
    parser.add_argument(
        "--clang_Oz_runset", action="store_true", help="Run clang -Oz option comparison"
    )
    args = parser.parse_args()

    runsets = []
    if args.gcc_Os_runset:
        runsets.append(gcc_Os_runset)
    if args.clang_Os_runset:
        runsets.append(clang_Os_runset)
    if args.clang_Oz_runset:
        runsets.append(clang_Oz_runset)

    run_all(runsets, args)


if __name__ == "__main__":
    sys.exit(main())
