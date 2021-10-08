#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# splitcsv.py


from typing import List, Iterable, Iterator

import csv
from pathlib import Path
from random import shuffle as random_shuffle


def _shuffle(iterable: Iterable) -> Iterator:
    """shuffle the given iterable"""
    result = list(iterable)
    random_shuffle(result)  # renamed random.shuffle
    return iter(result)


def split_csv(csvfile: Path,
              outdir: Path = None,
              splitnum: int = 2,
              rename: Iterable = None,
              prefix: str = '',
              shuffle: bool = False) -> None:
    """
    Split the given CSV-file evenly into the given number of parts

    :param csvfile: Original CSV-file to split up into `splitnum` parts
    :type csvfile: Path or str
    :param outdir: Directory where to save the split up parts into
                   Default: directory of the CSV-file
    :type outdir: Path or str
    :param splitnum: Numbers of splits to be made
                     Default: 2
    :type splitnum: int
    :param rename: List of strings holding the filenames for the new CSV-files
                   If given this also dictates the number of splits to be made
                   Default: None
    :type rename: List[str]
    :param prefix: Optional prefix to give to the new CSV-files
                   Default: no prefix
    :type prefix: str
    :param shuffle: Optional prefix to give to the new CSV-files
                   Default: no shuffle
    :type shuffle: bool
    :return: Nothing is returned
    :rtype: None
    """
    # contracts
    # make sure the given CSV-file is a file that exists
    csvfile = Path(csvfile)
    assert csvfile.is_file() and csvfile.exists(), f"csvfile can't be used, given: {csvfile}"
    # assure that the output directory exists
    if outdir is None:
        outdir = csvfile.parent
    assert Path(outdir).is_dir() and Path(outdir).exists(), "outdir can't be used"
    # if rename is not given, create filenames
    if rename is None and not bool(rename):
        rename = (f"{csvfile.stem}{num}" for num in range(1, (splitnum + 1)))
    else:  # make sure the given list contains strings, and set the length of the list to splitnum
        assert isinstance(rename, Iterable), "rename must be of type: Iterable[str]"
        assert all((isinstance(name, str) for name in rename)), \
            "objects in the rename iterable must be of type: str"
        # check new filenames on the most basic filename limitations
        assert not any(((set(name).intersection(set(r'\/:*?"<>|')) or name == 'null') for name in rename)), \
            "detected a reserved character in a filename"
        splitnum = len(rename)
    # check the number of splits
    assert splitnum >= 2, f"splitnum must be more or equal than 2, given: {splitnum}"

    # open the given CSV-file in read-mode
    with Path(csvfile).open('r', newline='') as given_csv:
        # get the headers (move cursor to next row)
        headers = next(csv.reader(given_csv))
        # calculate the rows with value in the CSV-file
        file_length = len([1 for _ in csv.reader(given_csv) if _])
        # calculate when to split the file
        row_split = int(file_length / splitnum)
        # assure that the file can be split up
        assert row_split > 0, f"csvfile can't be split up, {splitnum} is larger than the available rows"

        # reset cursor to start of file
        given_csv.seek(0)
        # read the rows of the CSV-file as a dict where the keys are the headers
        csv_row = csv.DictReader(given_csv, fieldnames=headers)
        next(csv_row)  # don't read the headers

        if bool(shuffle):
            csv_row = _shuffle(csv_row)  # shuffle the rows

        # create and fill the CSV-files
        for filename in rename:
            # add the path, prefix and suffix to the filename
            filepath = Path(outdir).joinpath(f"{prefix}{filename}{csvfile.suffix}")

            # open the created filepath in (over)write-mode
            with filepath.open('w', newline='') as new_file:
                csv_writer = csv.DictWriter(new_file, fieldnames=headers)
                csv_writer.writeheader()

                # write the row_split amount of rows into the new file
                for row_num, row in enumerate(csv_row, start=1):
                    csv_writer.writerow(row)
                    if row_split == row_num:
                        break  # next file
    # end split_csv


if __name__ == '__main__':
    import sys
    import textwrap
    import argparse
    from argparse import RawTextHelpFormatter

    # to parse the given arguments
    parser = argparse.ArgumentParser(
        prog=Path(__file__).name,
        usage='python %(prog)s </path/to/file.csv> [options] (-n | -r)',
        formatter_class=RawTextHelpFormatter,
        description=textwrap.dedent(
            """
        This script splits the given CSV-file evenly into a given count of parts.

        Be aware!
            It is assumed that the original CSV-file has headers.
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
            """
        )
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
                        type=str,
                        default='',
                        help="prefix for file names, default: nothing")
    parser.add_argument("-s", "--shuffle",
                        action='store_true',  # if given shuffle becomes true
                        help="shuffle the output, default: no shuffle")
    # mutual exclusive (can't choose both)
    mutex = parser.add_mutually_exclusive_group(required=False)
    mutex.add_argument("-n", "--splitnum",
                       default=2,  # this is the split amount if nothing is given
                       type=int,
                       help="n-times to split, default: 2")
    mutex.add_argument("-r", "--rename",
                       action='store',
                       default=None,
                       nargs='+',  # Error if only 1 name is given.
                       type=str,
                       help="names for the new files, minimal arguments: 2")

    # parse the arguments
    args = parser.parse_args()
    # expected_arguments = ('csvfile', 'splitnum', 'outdir', 'prefix', 'shuffle', 'rename')

    # assures that the splitnum is the length of the given number of renames
    if args.rename is not None:
        args.splitnum = len(args.rename)

    # if no outdir is given, make the outdir be the parent of the given csvfile
    args.outdir = args.outdir or Path(args.csvfile).parent

    if not Path(args.csvfile).is_file() or not Path(args.csvfile).exists():
        sys.stderr.write("given csvfile is not a file")
        exit(1)
    elif not Path(args.outdir).is_dir() or not Path(args.outdir).exists():
        sys.stderr.write("given outdir is not a directory")
        exit(2)
    elif args.rename is not None and args.splitnum < 2:
        sys.stderr.write(f"total given names is less than 2, given: {args.splitnum}")
        exit(3)
    elif args.splitnum < 2:
        sys.stderr.write(f"given splitnum is less than 2, given: {args.splitnum}")
        exit(4)
    else:
        split_csv(
            csvfile=args.csvfile,
            splitnum=args.splitnum,
            outdir=args.outdir,
            rename=args.rename,
            prefix=str(args.prefix),
            shuffle=bool(args.shuffle)
        )
