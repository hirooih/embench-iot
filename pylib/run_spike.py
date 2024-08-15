#!/usr/bin/env python3

# Python module to run programs on a spike simulator

# Copyright (C) 2023 Embecosm Limited
#
# Contributor: Hiroo Hayashi <hirooih@gmail.com>
#
# This file is part of Embench.

# SPDX-License-Identifier: GPL-3.0-or-later

"""
Embench module to run benchmark programs.

This version is suitable for a gdbserver with simulator.
"""

__all__ = [
    'get_target_args',
    'build_benchmark_cmd',
    'decode_results',
]

import argparse
import re

from embench_core import log


def get_target_args(remnant):
    """Parse left over arguments"""
    parser = argparse.ArgumentParser(description='Get target specific args')

    parser.add_argument(
        '--spike-command',
        type=str,
        default='spike',
        help='Command to invoke Spike',
    )
    parser.add_argument(
        '--spike-pk',
        type=str,
        default='pk',
        help='The RISC-V Proxy Kernel, pk, for Spike',
    )
    parser.add_argument(
        '--spike-args',
        type=str,
        default='',
        help='Arguments for Spike',
    )

    return parser.parse_args(remnant)


def build_benchmark_cmd(bench, args):
    """Construct the command to run the benchmark.  "args" is a
       namespace with target specific arguments"""
    return [f'{args.spike_command}'] + args.spike_args.split() + [f'{args.spike_pk}', bench]


def decode_results(stdout_str, stderr_str):
    """Extract the results from the output string of the run. Return the
       elapsed time in milliseconds or zero if the run failed."""
    # Return code is in standard output. We look for the string that means we
    # hit a breakpoint on _exit, then for the string returning the value.
    # mcycle
    rcstr = re.search('^cycle = 0x(\w+)', stdout_str, re.M)
    if not rcstr:
        log.debug('Warning: Failed to find cycle value')
        return 0.0
    cycle = int(rcstr.group(1), 16)
    # cycle @1MHz clock
    ms_elapsed = float(cycle) / 1000.0
    return ms_elapsed
