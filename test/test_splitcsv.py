#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# splitcsv.py

# python -m unittest discover --verbose --catch --start-directory ./test

import csv
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from splitcsv import split_csv


TESTCSV = Path(__file__).parent.joinpath('test.csv')
TESTCSV_ROWS = 100  # excl. headers


class TestSplitCSV(unittest.TestCase):

    def test_splitcsv_even_split_rowcount(self):
        splitcount = 2
        expected = int(TESTCSV_ROWS / splitcount)  # 50 * 2 = 100
        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            # split
            split_csv(TESTCSV, outdir=tempdir, splitnum=splitcount)
            # check
            for file in Path(tempdir).iterdir():
                with file.open('r') as split_file:
                    reader = csv.reader(split_file)
                    rowcount = int(len([1 for _ in reader]) - 1)  # don't count the header
                    self.assertEqual(expected, rowcount)

    def test_splitcsv_uneven_split_rowcount(self):
        splitcount = 3
        expected = int(TESTCSV_ROWS / splitcount)  # 33 * 3 = 99
        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            # split
            split_csv(TESTCSV, outdir=tempdir, splitnum=splitcount)
            # check
            for file in Path(tempdir).iterdir():
                with file.open('r') as split_file:
                    reader = csv.reader(split_file)
                    rowcount = int(len([1 for _ in reader]) - 1)  # don't count the header
                    self.assertEqual(expected, rowcount)

    def test_splitcsv_prefix(self):
        prefix = 'test_'
        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            # split
            split_csv(TESTCSV, outdir=tempdir, prefix=prefix)
            # check
            for file in Path(tempdir).iterdir():
                self.assertTrue(str(file.name).startswith(prefix))

    def test_splitcsv_file_numbering(self):
        splitcount = 5
        strnumbers = tuple(map(str, range(1, (splitcount + 1))))
        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            # split
            split_csv(TESTCSV, outdir=tempdir, splitnum=splitcount)
            # check
            for file in Path(tempdir).iterdir():
                # take last character of 'test1' -> '1'
                self.assertIn(str(file.stem)[-1], strnumbers)


if __name__ == '__main__':
    unittest.main(verbosity=2, catchbreak=True)
