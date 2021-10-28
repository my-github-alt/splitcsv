#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_arguments.py

# python -m unittest discover --verbose --catch --start-directory ./test

import io
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from splitcsv import main, split_csv

TESTCSV = Path(__file__).parent.joinpath('test.csv')
TESTCSV_ROWS = 100  # excl. headers


class TestSplitCSV(unittest.TestCase):

    def test_main_no_args(self):
        error = 'usage: python splitcsv.py </path/to/file.csv> [options] (-n | -r)\n' \
                'splitcsv.py: error: the following arguments are required: csvfile\n'
        with redirect_stderr(io.StringIO()) as stderr:
            with self.assertRaises(SystemExit):
                main(argv=None, function=None)
            self.assertEqual(stderr.getvalue(), error)

    def test_main_mutually_exclusive_args(self):
        argv = [str(TESTCSV), '--splitnum', '2', '--rename', 'a', 'b']
        error = 'usage: python splitcsv.py </path/to/file.csv> [options] (-n | -r)\n' \
                'splitcsv.py: error: argument -r/--rename: not allowed with argument -n/--splitnum\n'
        with redirect_stderr(io.StringIO()) as stderr:
            with self.assertRaises(SystemExit):
                main(argv=argv)
            self.assertEqual(stderr.getvalue(), error)

    def test_main_only_csvfile(self):
        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            tempdir = Path(tempdir)
            tempcsv = tempdir.joinpath(TESTCSV.name)
            shutil.copy(str(TESTCSV), str(tempcsv))
            argv = [str(tempcsv)]  # only give csv file
            err_num = main(argv=argv, function=split_csv)
            self.assertEqual(0, err_num)
            files_created = list(tempdir.iterdir())
            self.assertEqual(3, len(files_created))  # 3 files (2 made, one TESTCSV)

    def test_main_rename(self):
        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            tempdir = Path(tempdir)
            tempcsv = tempdir.joinpath(TESTCSV.name)
            shutil.copy(str(TESTCSV), str(tempcsv))
            argv = [str(tempcsv), '--rename', 'a', 'b', 'c']  # only give csv file
            err_num = main(argv=argv, function=split_csv)
            self.assertEqual(0, err_num)
            files_created = list(tempdir.iterdir())
            self.assertEqual(4, len(files_created))  # 4 files (3 made, one TESTCSV)

    def test_main_splitnum(self):
        with TemporaryDirectory(prefix='csv_test_', suffix='_dir') as tempdir:
            tempdir = Path(tempdir)
            tempcsv = tempdir.joinpath(TESTCSV.name)
            shutil.copy(str(TESTCSV), str(tempcsv))
            argv = [str(tempcsv), '--splitnum', '5']  # only give csv file
            err_num = main(argv=argv, function=split_csv)
            self.assertEqual(0, err_num)
            files_created = list(tempdir.iterdir())
            self.assertEqual(6, len(files_created))  # 6 files (5 made, one TESTCSV)


if __name__ == '__main__':
    unittest.main(verbosity=2, catchbreak=True)
