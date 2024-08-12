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
import subprocess
import sys
import textwrap

sys.path.append(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'pylib')
)

from embench_core import check_python_version
from embench_core import log
from embench_core import arglist_to_str

# What we export

__all__ = [
    'build_parser',
    'run_all',
]


def build_parser():
    """Build a parser for all the arguments"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(f'''\
            Build and run all the benchmarks.

            # A typical run
            {sys.argv[0]} --<run-set>

            You may wish to run speed benchmarks in batch processes, record the results in a log file,
            and collect the benchmark results from the log.

            In such a case, do the following:

            # Build and run the speed benchmark
            {sys.argv[0]} --no-size --<run-set>
            # Build and collect size benchmarks, and collect speed benchmarks
            {sys.argv[0]} --no-build-for-speed  --<run-set>
            '''))

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
        '--no-size',
        action='store_true',
        help='Disable the size benchmark.')
    parser.add_argument(
        '--no-build-for-speed',
        action='store_true',
        help='Disable the build for speed benchmark.')

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
        '--timeout=30',     # The default value (5sec) is to short for LTO.
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
    if os.path.isabs(path):
        install_dir = os.path.abspath(os.path.join(
            path,
        ))
    else:
        install_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            path,
            'bin'   # remains for backward compatibility
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


def run_all(runsets, args):
    """run the all runsets"""
    # Make sure we have new enough Python and only run if this is the main package
    check_python_version(3, 6)

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
            if not args.no_size and 'size benchmark' in rs:
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
                    cflags=r.get('cflags') + " -DSIZE_BENCHMARK",
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
                if not args.no_build_for_speed:
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
                        cflags=r.get('cflags') + " -DSPEED_BENCHMARK",
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
