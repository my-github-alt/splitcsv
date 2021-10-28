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


def get_rename(tempdir, splitnum):
    return [tempdir.joinpath(f"{TESTCSV.stem}{n}{TESTCSV.suffix}")
            for n in range(1, (splitnum + 1))]


class TestSplitCSV(unittest.TestCase):

    def test_splitcsv_even_split_rowcount(self):
        splitcount = 2
        expected = int(TESTCSV_ROWS / splitcount)  # 50 * 2 = 100
        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            tempdir = Path(tempdir)
            rename = get_rename(tempdir, splitcount)
            # split
            split_csv(TESTCSV, rename=rename)
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
            tempdir = Path(tempdir)
            rename = get_rename(tempdir, splitcount)
            # split
            split_csv(TESTCSV, rename=rename)
            # check
            for file in Path(tempdir).iterdir():
                with file.open('r') as split_file:
                    reader = csv.reader(split_file)
                    rowcount = int(len([1 for _ in reader]) - 1)  # don't count the header
                    self.assertEqual(expected, rowcount)

    def test_splitcsv_as_many_splits_as_rows(self):
        row_count = None
        with TESTCSV.open('r') as file:
            row_count = len(file.readlines()) - 1  # don't count the header

        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            tempdir = Path(tempdir)
            rename = get_rename(tempdir, row_count)
            # split
            split_csv(TESTCSV, rename=rename)
            self.assertEqual(len(tuple(Path(tempdir).iterdir())), row_count)  # check

    def test_splitcsv_split_too_many(self):
        row_count = None
        with TESTCSV.open('r') as file:
            row_count = len(file.readlines()) + 1

        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            tempdir = Path(tempdir)
            rename = get_rename(tempdir, row_count)
            with self.assertRaises(AssertionError):  # check
                split_csv(TESTCSV, rename=rename) # split



if __name__ == '__main__':
    unittest.main(verbosity=2, catchbreak=True)
