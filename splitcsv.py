#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# splitcsv.py


from typing import List, Iterable, Iterator, Callable
import argparse
import csv
from pathlib import Path
from textwrap import dedent
from random import shuffle as random_shuffle


def main(argv: List[str] = None, function: Callable = None) -> int:
    """commandline entry function"""

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

        Randomize the rows of the new created split up CSV-files
            python %(prog)s ./file.csv --shuffle -n 2
    """)

    parser = argparse.ArgumentParser(
        prog=Path(__file__).name,
        usage='python %(prog)s </path/to/file.csv> [options] (-n | -r)',
        formatter_class=argparse.RawTextHelpFormatter,
        description=description
    )
    # positional arguments (required)
    parser.add_argument("csvfile",
                        type=Path,
                        help="CSV-file to split")
    # optional arguments
    parser.add_argument("-o", "--outdir",
                        default=None,  # <- could become the parent-dir of csvfile
                        help="directory to place the new files, default: same as csvfile")
    parser.add_argument("-p", "--prefix",
                        default='',
                        type=str,
                        help="prefix for file names, default: nothing")
    parser.add_argument("-s", "--shuffle",
                        action='store_true',  # if given shuffle becomes true
                        help="shuffle the output, default: no shuffle")
    # mutual exclusive (can't choose both)
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

    # parse the given arguments
    args: argparse.Namespace = parser.parse_args(args=argv)

    # give the arguments some default values
    if args.splitnum is None:
        args.splitnum = 2  # assure the splitnum is at least 2
    if args.outdir is None:
        args.outdir = args.csvfile.parent  # set the parent of the csv-file as the output directory
    else:
        args.outdir = Path(args.outdir)
    if args.rename is None:  # create new file paths and new names
        args.rename = [args.outdir.joinpath(f"{args.prefix}{args.csvfile.stem}{n}{args.csvfile.suffix}")
                       for n in range(1, (args.splitnum + 1))]
    else:  # create file paths for the given names  (splitnum is not given)
        args.rename = [args.outdir.joinpath(f"{args.prefix}{n}{args.csvfile.suffix}")
                       for n in args.rename]

    # check if the arguments are as expected
    if not args.csvfile.exists():
        print(f"{args.csvfile} doesn't exist")
        return 101  # exit
    if not args.outdir.exists():
        print(f"{args.outdir} doesn't exist")
        return 102  # exit
    if not args.outdir.is_dir():
        print(f"{args.outdir} is not a directory")
        return 103  # exit
    if not args.splitnum >= 2:
        print(f"given splitnumber is less than 2, given: {args.splitnum}")
        return 104  # exit
    if not len(args.rename) >= 2:
        print(f"given renames is less than 2, given: {len(args.rename)}")
        return 105  # exit

    # unpack the arguments as a dict into the given function
    if function is not None:
        function(**vars(args))

    return 0  # exit


def _shuffle(iterable: Iterable) -> Iterator:
    """shuffle the given iterable"""
    result = list(iterable)
    random_shuffle(result)  # renamed random.shuffle  -  shuffles in-place
    return iter(result)


def _sniff_csv(csvfile: Path) -> [csv.Dialect, List]:
    """sniff the Dialect and the headers of the CSV-file"""
    with csvfile.open('r', newline='') as fd:
        sniffer = csv.Sniffer()
        [fd.readline() for _ in range(10)]  # doesn't go wrong when file is less than 10 lines
        ten_rows = fd.tell()  # get the position of the cursor after 10 rows has been read
        fd.seek(0)  # reset cursor
        dialect = sniffer.sniff(fd.read(ten_rows))
        fd.seek(0)
        headers = []
        if sniffer.has_header(fd.read(ten_rows)):
            fd.seek(0)
            headers: list = next(csv.reader(fd, dialect=dialect))
    return dialect, headers


def split_csv(csvfile: Path, rename: Iterable[Path], shuffle: bool = False, **kwargs) -> None:
    """Split the given CSV-file evenly into the given number of parts

    :param csvfile: Original CSV-file to split up into parts
    :type csvfile: Path
    :param rename: List of strings holding the filenames for the new CSV-files
                   If given this also dictates the number of splits to be made
    :type rename: List[Path]
    :param shuffle: Optional prefix to give to the new CSV-files
                   Default: no shuffle
    :type shuffle: bool
    :return: Nothing is returned
    :rtype: None
    """
    # sniff out the dialect and the headers of the CSV-file
    dialect, headers = _sniff_csv(csvfile)
    # get the number of new files
    splitnum = len(list(rename))
    # open the given CSV-file in read-mode
    with Path(csvfile).open('r', newline='') as given_csv:
        if len(headers) > 0:
            given_csv.readline()  # ignore headers headers
        # calculate the rows with value in the CSV-file
        file_length = len([1 for _ in csv.reader(given_csv) if _])
        # calculate when to split the file
        row_split = int(file_length / splitnum)
        # assure that the file can be split up
        assert row_split > 0, f"csvfile can't be split up, {splitnum} is larger than the available rows"

        # reset cursor to start of file
        given_csv.seek(0)

        # read the rows of the CSV-file as a dict where the keys are the headers
        csv_row = csv.reader(given_csv, dialect=dialect)
        if len(headers) > 0:
            next(csv_row)  # don't read the headers

        if bool(shuffle):
            csv_row = _shuffle(csv_row)  # shuffle the rows

        # create and fill the CSV-files
        for filepath in rename:
            # open the created filepath in (over)write-mode
            with Path(filepath).open('w', newline='') as new_file:
                csv_writer = csv.writer(new_file, dialect=dialect)
                if len(headers) > 0:
                    csv_writer.writerow(headers)
                # write the row_split amount of rows into the new file
                for row_num, row in enumerate(csv_row, start=1):
                    csv_writer.writerow(row)
                    if row_num >= row_split:
                        break  # next file
    # end split_csv


if __name__ == '__main__':
    raise SystemExit(
        main(function=split_csv)
    )
