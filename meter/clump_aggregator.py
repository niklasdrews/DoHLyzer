#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path


class ClumpAggregator:
    """Aggregates multiple JSON or CSV clump files into a single file."""

    def __init__(self, input_dir: str, output_format: str):
        """
        Initialize the ClumpAggregator.

        Args:
            input_dir: Directory containing the files to aggregate
            output_format: Either '--json' or '--csv' to specify output format
        """
        self.input_dir = input_dir
        # Handle both '--json' and 'json' formats
        self.file_type = output_format.replace('--', '')

        if self.file_type not in ['json', 'csv']:
            raise ValueError(
                f"Invalid output format: {output_format}. Must be '--json' or '--csv'")

    def aggregate_clumps(self) -> Path:
        """Aggregate all clump files in the input directory into a single file."""
        path = self.input_dir
        file_type = self.file_type

        # Get all files of the specified type, excluding the output file
        files = [os.path.join(path, f) for f in os.listdir(path) if
                 f.endswith(f".{file_type}") and not f == f'all.{file_type}']

        if file_type == 'json':
            return self._aggregate_json(files, path)
        else:
            return self._aggregate_csv(files, path)

    def _aggregate_json(self, files: list, path: str) -> Path:
        """Aggregate JSON files into all.json."""
        result_file = Path(path) / 'all.json'
        out = open(result_file, 'w')
        out.write('[\n')
        for file_num, file_path in enumerate(files):
            try:
                print('[{}/{}] {}'.format(file_num, len(files), file_path))
                f = open(file_path, 'r')
                f_c = json.load(f)
                if file_num != 0:
                    out.write(',\n')
                out.write(',\n'.join(json.dumps(obj) for obj in f_c))
                f.close()
            except json.JSONDecodeError:
                print('ERROR')

        out.write(']\n')
        out.close()
        return Path(result_file)

    def _aggregate_csv(self, files: list, path: str) -> Path:
        """Aggregate CSV files into all.csv."""
        result_file = Path(path) / 'all.csv'
        out = open(result_file, 'w')
        contents = list()
        for file_num, file_path in enumerate(files):
            f = open(file_path, 'r')
            for line_num, line in enumerate(f):
                if line_num == 0 and file_num != 0:
                    continue
                contents.append(line)
            print(file_num, file_path)
        out.writelines(contents)
        out.close()
        return Path(result_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--json', dest='file_type',
                       action='store_const', const='json')
    group.add_argument('--csv', dest='file_type',
                       action='store_const', const='csv')
    args = parser.parse_args()

    # Use the ClumpAggregator class
    aggregator = ClumpAggregator(
        input_dir=args.input_dir,
        output_format=f'--{args.file_type}'
    )
    aggregator.aggregate_clumps()
