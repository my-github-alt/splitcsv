#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# splitcsv.py


import csv
from pathlib import Path


def split_csv(csvfile: Path, outdir: Path = None, splitnum: int = 2, prefix: str = '') -> None:
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
    :param prefix: Optional prefix to give to the new CSV-files
                   Default: no prefix
    :type prefix: str
    :return: Nothing is returned
    :rtype: None
    """
    # assertions
    csvfile = Path(csvfile)
    assert csvfile.is_file() and csvfile.exists(), f"csvfile can't be used, given: {csvfile}"
    assert splitnum >= 2, f"splitnum must be more or equal than 2, given: {splitnum}"
    if outdir is None:
        outdir = csvfile.parent
    assert Path(outdir).is_dir() and Path(outdir).exists(), "outdir can't be used"

    # calculate the rows with value in the CSV-file ( -1 don't count the headers )
    file_length = int(len([1 for _ in csv.reader(csvfile.open('r', newline='')) if _]) - 1)
    # calculate when to split the file
    row_split = int(file_length / splitnum)
    # assure that the file can be split up
    assert row_split > 0, f"csvfile can't be split up, {splitnum} is larger than the available rows"
    # get the headers
    headers = next(csv.reader(csvfile.open('r', newline='')))

    # open the given CSV-file in read-mode
    with Path(csvfile).open('r', newline='') as given_csv:
        # read the rows of the CSV-file as a dict where the keys are the headers
        csv_row = csv.DictReader(given_csv, fieldnames=headers)
        next(csv_row)  # don't read the headers

        # create and fill the CSV-files
        for file_num in range(1, (splitnum + 1)):
            filename = f"{prefix}{csvfile.stem}{file_num}{csvfile.suffix}"
            filepath = Path(outdir).joinpath(filename)

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
        usage='python %(prog)s </path/to/file.csv> [options]',
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
                Split CSV-file in 2 parts and save parts to relative directory
                    python %(prog)s ./file.csv -o ./out/dir/
                Give the split up CSV-files a prefix which result to: Prefix_file1.csv, etc.
                    python %(prog)s ./file.csv -p Prefix_
            """
        )
    )
    # positional arguments (required)
    parser.add_argument("csvfile",
                        type=Path,
                        help="CSV-file to split")
    # optional arguments
    parser.add_argument("-n", "--splitnum",
                        type=int,
                        default=2,
                        help="n-times to split, default: 2")
    parser.add_argument("-o", "--outdir",
                        default=None,  # <- could become the parent-dir of csvfile
                        help="directory to place the new files, default: same as csvfile")
    parser.add_argument("-p", "--prefix",
                        type=str,
                        default='',
                        help="prefix for file names, default: nothing")

    # parse the arguments
    args = parser.parse_args()
    # expected_arguments = ('csvfile', 'splitnum', 'outdir', 'prefix')

    # if no outdir is given, make the outdir be the parent of the given csvfile
    args.outdir = args.outdir or Path(args.csvfile).parent

    if not Path(args.csvfile).is_file() or not Path(args.csvfile).exists():
        sys.stderr.write("given csvfile is not a file")
        exit(1)
    elif not Path(args.outdir).is_dir() or not Path(args.outdir).exists():
        sys.stderr.write("given outdir is not a directory")
        exit(2)
    elif args.splitnum < 2:
        sys.stderr.write(f"given splitnum is less than 2, given: {args.splitnum}")
        exit(3)
    else:
        split_csv(
            csvfile=args.csvfile,
            splitnum=args.splitnum,
            outdir=args.outdir,
            prefix=str(args.prefix)
        )
