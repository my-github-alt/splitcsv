#!/usr/bin/python3
# -*- coding: utf-8 -*-
# splitcsv.py

from __future__ import annotations
from collections.abc import Sequence
from typing import Union, NewType, Optional

import argparse
import csv
import logging
from itertools import cycle
from pathlib import Path
from textwrap import dedent

FilePath = NewType('File', Union[str, Path])

logger = logging.getLogger(__name__)


def _sniff_csv(csvfile: FilePath) -> [csv.Dialect, list[str]]:
    """sniff the Dialect and the headers of the CSV-file"""
    with Path(csvfile).open('r', newline='') as fd:
        sniffer = csv.Sniffer()
        [fd.readline() for _ in range(10)]  # doesn't go wrong when file is less than 10 lines
        ten_rows = fd.tell()  # get the position of the cursor after 10 rows has been read
        fd.seek(0)  # reset cursor
        dialect = sniffer.sniff(fd.read(ten_rows))
        fd.seek(0)
        headers = []
        if sniffer.has_header(fd.read(ten_rows)):
            fd.seek(0)
            headers: list[str] = next(csv.reader(fd, dialect=dialect))
    return dialect, headers


def parse_arguments(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """parse the given arguments"""
    description = dedent("""
        This script splits the given CSV-file evenly into a given count of parts.

        Be aware!
            Can't split up the CSV-file if number of splits are larger than available rows.
            If split results into an uneven split, rows (multiple) can be discarded.

        Examples:
            Split CSV-file in 3 parts
                python %(prog)s /path/to/file.csv -n 3

            Name the output files. (example output: ./A.csv and ./B.csv)
                python %(prog)s ./file.csv -r A B

            Split CSV-file in 2 parts and save parts to relative directory
                python %(prog)s ./file.csv -o ./out/dir/

            Give the split up CSV-files a prefix (example output: ./csv_file1.csv, etc.)
                python %(prog)s ./file.csv -p csv_
        """)

    parser = argparse.ArgumentParser(
        prog=Path(__file__).name,
        usage='python %(prog)s </path/to/file.csv> [options] (-n | -r)',
        formatter_class=argparse.RawTextHelpFormatter,
        description=description
    )

    # required argument
    parser.add_argument("csvfile",
                        type=Path,
                        help="CSV-file to split")

    # split options
    mutex = parser.add_mutually_exclusive_group(required=False)
    mutex.add_argument("-n", "--splitnum",
                       default=None,  # this is the split amount if nothing is given
                       type=int,
                       help="n-times to split, default: 2")
    mutex.add_argument("-r", "--rename",
                       default=None,
                       type=str,
                       action='store',
                       nargs='+',  # Error if only 1 name is given.
                       help="names for the new files, minimal arguments: 2")

    # optional options
    options = parser.add_argument_group(title='optional')
    options.add_argument("-o", "--outdir",
                         default=None,  # <- could become the parent-dir of csvfile
                         type=Path,
                         help="directory to place the new files, default: same as csvfile")
    options.add_argument("-p", "--prefix",
                         default='',
                         type=str,
                         help="prefix for file names, default: nothing")

    # parse the given arguments
    args: argparse.Namespace = parser.parse_args(args=argv)

    # assure `args.outdir` is defined
    if args.outdir is None:
        args.outdir = args.csvfile.parent

    # fill `args.rename` with Paths
    suffix = args.csvfile.suffix
    if args.rename is not None:
        args.rename = [args.outdir.joinpath(f'{args.prefix}{name}{suffix}')
                       for name in args.rename]
    else:
        args.splitnum = args.splitnum or 2
        args.rename = [args.outdir.joinpath(f'{args.prefix}{args.csvfile.stem}{i}{suffix}')
                       for i in range(args.splitnum)]
        
    # splitnum and length of rename list should be the same
    args.splitnum = len(args.rename)

    # log arguments
    for key, value in vars(args).items():
        logger.debug(f'argument {key}: {value!r}')

    return args


def split_csv(original: FilePath, new_files: Sequence[FilePath], sniff: bool = False) -> None:
    """split the `original` CSV-file into the given `new_files`

    :param original: Original CSV-file
    :type original: FilePath
    :param new_files: List of filepaths where to write the CSV-rows to
    :type new_files: Sequence[FilePath]
    :param sniff: Checks dialect and captures the header of the CSV-file
    :type sniff: bool
    :return: Nothing is returned
    :rtype: None
    """
    # sniff for dialect and headers
    dialect, headers = _sniff_csv(original) if sniff else ('excel', [])
    logging.debug(f'dialect: {dialect}')
    logging.debug(f'headers: {headers}')

    # read the original
    with Path(original).open('r', newline='') as open_fd:
        csv_reader = csv.reader(open_fd, dialect=dialect)
        file_length = len(list(csv_reader))
        open_fd.seek(0)

        # create file descriptors and CSV-writers
        open_files = [Path(fd).open('w', newline='') for _, fd in zip(range(file_length), new_files)]
        csv_writers = [csv.writer(fd, dialect=dialect) for _, fd in zip(range(file_length), open_files)]

        if headers:  # write headers received by _sniff_csv
            for csv_writer in csv_writers:
                csv_writer.writerow(headers)

        try:  # split the lines over the number of given files
            for csv_writer, row in zip(cycle(csv_writers), csv_reader):
                if not row:
                    continue
                csv_writer.writerow(row)  # cycle split's the file
        except Exception as err:
            logger.exception(err)
            raise err
        finally:  # always close files
            for fd in open_files:
                fd.close()


def main(argv: Optional[list[str]] = None):
    args: argparse.Namespace = parse_arguments(argv)
    split_csv(args.csvfile, args.rename, sniff=True)
    return 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    raise SystemExit(main())