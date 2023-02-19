#!/usr/bin/env python3
#
# Copyright (C) 2023 Hiroo Hayashi <hirooih@gmail.com>
#
# SPDX-License-Identifier: GPL-2.0-or-later

import os
import sys
import argparse
import json

import matplotlib.pyplot as plt
import numpy as np


class embenchPlot:
    """
    Plot results of Embench from JSON format output files.
    usage: embench_plot --help
    """

    def extract(self, input, type):
        """ Simplify redundant data structures. """
        out = {}
        out['dr'] = input[f'{type} results'][f'detailed {type} results']
        out['gm'] = input[f'{type} results'][f'{type} geometric mean']
        out['gsd'] = input[f'{type} results'][f'{type} geometric standard deviation']
        return out

    def show(self, plt, fname):
        if self.args.image:
            try:
                plt.savefig(os.path.join(self.args.image_dir, fname))
            except FileNotFoundError as e:
                print(e)
                sys.exit(1)
        else:
            plt.show()

    def title_prefix(self):
        return f'{self.title}: ' if self.title else ''

    def title_gm_gsd(self, type):
        return f"{self.title_prefix()}{self.mode.capitalize()} {type.capitalize()} Score"

    def plot_gm_gsd(self, d, type, xticks_rotation=10):
        """Plot Geometric Means and Geometric Standard Deviations."""
        fig, ax = plt.subplots(constrained_layout=True)
        plt.bar(d.keys(),
                [v['gm'] for k, v in d.items()],
                yerr=[v['gsd'] - 1.0 for k, v in d.items()], capsize=10)
        plt.xticks(rotation=xticks_rotation)
        plt.title(self.title_gm_gsd(type))
        self.show(plt, f"gm_gsd-{self.mode}-{type}.svg")

    def title_each_result(self, key, type):
        return f"{self.title_prefix()}{key}: {self.mode.capitalize()} {type.capitalize()}"

    def plot_per_run(self, dr, key, type, xticks_rotation=90):
        """Plot detailed results."""
        fig, ax = plt.subplots(constrained_layout=True)
        plt.bar(dr.keys(), dr.values())
        plt.xticks(rotation=xticks_rotation)
        plt.title(self.title_each_result(key, type))
        self.show(plt, f"detail-{self.mode}-{type}-{key}.svg")

    def title_grouped_bar(self, type):
        return f"{self.title_prefix()}{self.mode.capitalize()} {type.capitalize()}"

    def plot_grouped(self, groups, results, type, xticks_rotation=10):
        # Grouped bar chart with labels
        # https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py

        x = np.arange(len(groups))  # the label locations
        width = 1 / (len(results) + 1)  # the width of the bars

        fig, ax = plt.subplots(constrained_layout=True)

        i = 0
        for attribute, measurement in results.items():
            ax.bar(x + width * i, measurement, width, label=attribute)
            i += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(f"{self.mode.capitalize()} {type.capitalize()}")
        ax.set_title(self.title_grouped_bar(type))
        ax.set_xticks(x + 0.4, groups, rotation=xticks_rotation)
        ax.legend(loc='upper left', ncols=2)

        self.show(plt, f"grouped-{self.mode}-{type}.svg")

    def plot_all_sub(self, d, type):
        """
        type: "size" or "speed"
        """
        print(type)
        for k, v in d.items():
            print(f"{k}\t{v['gm']:.2f}\t{v['gsd']:.2f}")
        self.plot_gm_gsd(d, type, self.xticks_rotation_gm_gsd)

        if self.args.plot_each_result:
            for k, v in d.items():
                self.plot_per_run(v['dr'], k, type, self.xticks_rotation_per_run)

        runs = list(d.keys())
        benches = list(d[runs[0]]['dr'].keys())

        results = {}
        for k, v in d.items():
            results[k] = []
            for bench in benches:
                results[k].append(v['dr'][bench])
        self.plot_grouped(benches, results, type, self.xticks_rotation_grouped_benchmark)

        # results = {}
        # for bench in benches:
        #     results[bench] = []
        #     for v in d.values():
        #         results[bench].append(v['dr'][bench])
        # self.plot_grouped(runs, results, type, self.xticks_rotation_grouped_run)

    def plot_all(self, d):
        if d['size']:
            self.plot_all_sub(d['size'],  'size')
        if d['speed']:
            self.plot_all_sub(d['speed'], 'speed')

    def build_parser(self):
        """Build a parser for all the arguments"""
        parser = argparse.ArgumentParser(description='Plot the results of the EmBench benchmark.')
        parser.add_argument('--title', help='Title of the plot')
        parser.add_argument('--mode', choices=['relative', 'absolute'], default='relative',
                            help='Mode of benchmark.')
        parser.add_argument('--image', action="store_true",
                            help='generating SVG files, in stead of viewing on display.')
        parser.add_argument('--image-dir', default='images',
                            help='Name of the directory where the SVG files are saved.')
        parser.add_argument('files', metavar='file', nargs='*',
                            help='Embench output file[s] in JSON format.')
        parser.add_argument('--plot-each-result', action="store_true", help='plot each benchmark result.')
        return parser

    def parse_args(self):
        self.args = self.build_parser().parse_args()
        # Make frequently used items class variables.
        self.title = self.args.title
        self.mode = self.args.mode

    def run_name(self, file):
        '''
        Use basename of input file as a name of the run.
        This method may be overridden.
        '''
        return os.path.splitext(os.path.basename(file))[0]

    def __init__(self):
        self.args = []
        self.xticks_rotation_gm_gsd = 10
        self.xticks_rotation_per_run = 90
        self.xticks_rotation_grouped_benchmark = 90
        self.xticks_rotation_grouped_run = 10

    def main(self):
        self.parse_args()

        data = {'size': {}, 'speed': {}}
        files = self.args.files or ['-']
        for file in files:
            if file == '-':
                f = sys.stdin
            else:
                try:
                    f = open(file)
                except FileNotFoundError as e:
                    print(e, file=sys.stderr)
                    sys.exit(1)

            try:
                d = json.load(f)
            except json.JSONDecodeError:
                print(f"JSON format error in {file}. Ignored.", file=sys.stderr)
                sys.exit(1)

            # run names are used in graph.
            run = self.run_name(file)

            # Simplify redundant data structures.
            if 'size results' in d:
                data['size'][run] = self.extract(d, 'size')
            if 'speed results' in d:
                data['speed'][run] = self.extract(d, 'speed')

        # print(json.dumps(data, indent=4))
        self.plot_all(data)


if __name__ == "__main__":
    embenchPlot().main()

"""
// input data format
{
    "size results": {
        "detailed size results": {
            "aha-mont64": 0.65,
            ...
            "wikisort": 1.3
        },
        "size geometric mean": 1.23,
        "size geometric standard deviation": 1.31
    },
    "speed results": {
        "detailed speed results": {
            "aha-mont64": 0.65,
            ...
            "wikisort": 1.3
        },
        "speed geometric mean": 1.23,
        "speed geometric standard deviation": 1.31
    }
}
"""
