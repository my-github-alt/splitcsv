#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_arguments.py

# python -m unittest discover --verbose --catch --start-directory ./test

from __future__ import annotations
from argparse import Namespace

import io
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from splitcsv import parse_arguments

TESTCSV = Path(__file__).parent.joinpath('test.csv')
TESTCSV_ROWS = 100  # excl. headers


class TestSplitCSV(unittest.TestCase):

    def test_main_no_args(self):
        error = 'usage: python splitcsv.py </path/to/file.csv> [options] (-n | -r)\n' \
                'splitcsv.py: error: the following arguments are required: csvfile\n'
        with redirect_stderr(io.StringIO()) as stderr:
            with self.assertRaises(SystemExit):
                parse_arguments(argv=None)
            self.assertEqual(stderr.getvalue(), error)

    def test_main_mutually_exclusive_args(self):
        argv = [str(TESTCSV), '--splitnum', '2', '--rename', 'a', 'b']
        error = 'usage: python splitcsv.py </path/to/file.csv> [options] (-n | -r)\n' \
                'splitcsv.py: error: argument -r/--rename: not allowed with argument -n/--splitnum\n'
        with redirect_stderr(io.StringIO()) as stderr:
            with self.assertRaises(SystemExit):
                parse_arguments(argv=argv)
            self.assertEqual(stderr.getvalue(), error)

    def test_main_only_csvfile(self):
        filepath = 'test.csv'
        args: Namespace = parse_arguments([filepath])
        self.assertEqual(str(args.csvfile), filepath)
        self.assertEqual(args.splitnum, 2)
        self.assertEqual(len(args.rename), 2)
        self.assertEqual(str(args.outdir), '.')
        self.assertEqual(str(args.prefix), '')

    def test_main_rename(self):
        filepath = 'test.csv'
        filenames = ['A', 'B', 'C']
        args: Namespace = parse_arguments([filepath, '--rename', *filenames])
        self.assertEqual(str(args.csvfile), filepath)
        self.assertEqual(args.splitnum, 3)
        self.assertEqual(len(args.rename), 3)
        for name, path in zip(filenames, args.rename):
            self.assertEqual(path.stem, name)
        self.assertEqual(str(args.outdir), '.')
        self.assertEqual(str(args.prefix), '')

    def test_main_splitnum(self):
        filepath = 'test.csv'
        splitnum = 10
        args: Namespace = parse_arguments([filepath, '--splitnum', str(splitnum)])
        self.assertEqual(str(args.csvfile), filepath)
        self.assertEqual(args.splitnum, splitnum)
        self.assertEqual(len(args.rename), splitnum)
        for name, path in zip(range(splitnum), args.rename):
            self.assertEqual(path.stem, name)
        self.assertEqual(str(args.outdir), '.')
        self.assertEqual(str(args.prefix), '')


if __name__ == '__main__':
    unittest.main(verbosity=2, catchbreak=True)
