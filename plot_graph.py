#!/usr/bin/env python3
import json
from pylib.embench_plot import embenchPlot


class myEmbenchPlot(embenchPlot):
    def run_name(self, file, mode, title):
        return '<' + super().run_name(file, mode, title) + '>'

    def main(self):
        self.parse_args()

        self.title = 'macOS'
        runs = ['macos-O0', 'macos-Oz', 'macos-Os', 'macos-O2', 'macos-O3']

        data = {'size': {}, 'speed': {}}
        for run in runs:
            with open(f'results/{run}.json') as f:
                d = json.load(f)
                data['size'][run] = self.extract(d, 'size')
                data['speed'][run] = self.extract(d, 'speed')

        # print(json.dumps(data, indent=4))
        self.xticks_rotation_gm_gsd = 30
        self.plot_all(data)


if __name__ == "__main__":
    myEmbenchPlot().main()
