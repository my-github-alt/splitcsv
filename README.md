# splitcsv


🖥️ `python splitcsv.py -h`

```
usage: python splitcsv.py </path/to/file.csv> [options]

This script splits the given CSV-file evenly into a given count of parts.

Be aware!
    It is assumed that the original CSV-file has headers.
    Can't split up the CSV-file if number of splits are larger than available rows.
    If split results into an uneven split, rows (multiple) can be discarded.

Examples:
    Split CSV-file in 3 parts
        python splitcsv.py /path/to/file.csv -n 3
    Split CSV-file in 2 parts and save parts to relative directory
        python splitcsv.py ./file.csv -o ./out/dir/
    Give the split up CSV-files a prefix which result to: Prefix_file1.csv, etc.
        python splitcsv.py ./file.csv -p Prefix_

positional arguments:
  csvfile               CSV-file to split

optional arguments:
  -h, --help            show this help message and exit
  -n SPLITNUM, --splitnum SPLITNUM
                        n-times to split, default: 2
  -o OUTDIR, --outdir OUTDIR
                        directory to place the new files, default: same as csvfile
  -p PREFIX, --prefix PREFIX
                        prefix for file names, default: nothing
```
