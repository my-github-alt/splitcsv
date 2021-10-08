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

    def test_splitcsv_prefix_with_rename(self):
        prefix = 'test_'
        names = ('a', 'b')
        full_names = tuple(f'{prefix}{n}' for n in names)
        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            split_csv(TESTCSV, outdir=tempdir, rename=names, prefix=prefix)  # split
            for file in Path(tempdir).iterdir():
                self.assertTrue(str(file.name).startswith(prefix))  # check
                self.assertIn(file.stem, full_names)

    def test_splitcsv_rename_dictates_splitnum(self):
        names = ('a', 'b', 'c')
        num_of_splits = len(names)
        splitnum = num_of_splits - 1 
        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            split_csv(TESTCSV, outdir=tempdir, rename=names, splitnum=splitnum)  # check
            self.assertEqual(len(tuple(Path(tempdir).iterdir())), num_of_splits)  # check

    def test_splitcsv_file_numbering(self):
        splitcount = 5
        strnumbers = tuple(map(str, range(1, (splitcount + 1))))
        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            split_csv(TESTCSV, outdir=tempdir, splitnum=splitcount)  # split
            for file in Path(tempdir).iterdir():
                # take last character of 'test1' -> '1'
                self.assertIn(str(file.stem)[-1], strnumbers)  # check

    def test_splitcsv_as_many_splits_as_rows(self):
        row_count = None
        with TESTCSV.open('r') as file:
            row_count = len(file.readlines()) - 1  # don't count the header

        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            split_csv(TESTCSV, outdir=tempdir, splitnum=row_count)  # split
            self.assertEqual(len(tuple(Path(tempdir).iterdir())), row_count)  # check

    def test_splitcsv_split_too_many(self):
        row_count = None
        with TESTCSV.open('r') as file:
            row_count = len(file.readlines()) + 1

        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            with self.assertRaises(AssertionError):  # check
                split_csv(TESTCSV, outdir=tempdir, splitnum=row_count)  # split

    def test_splitcsv_split_too_less(self):
        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            # check
            with self.assertRaises(AssertionError):
                split_csv(TESTCSV, outdir=tempdir, splitnum=-1)
            with self.assertRaises(AssertionError):
                split_csv(TESTCSV, outdir=tempdir, splitnum=1)
            with self.assertRaises(AssertionError):
                split_csv(TESTCSV, outdir=tempdir, rename=[])
            with self.assertRaises(AssertionError):
                split_csv(TESTCSV, outdir=tempdir, rename=['1'])

    def test_splitcsv_rename_filename_limitations(self):
        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            with self.assertRaises(AssertionError):
                split_csv(TESTCSV, outdir=tempdir, rename=('test', 'null'))  # null is a faulty name
            for char in r'\/:*?"<>|':  # windows filename limitations
                with self.assertRaises(AssertionError):
                    split_csv(TESTCSV, outdir=tempdir, rename=('test', f'test_{char}_name'))


if __name__ == '__main__':
    unittest.main(verbosity=2, catchbreak=True)
