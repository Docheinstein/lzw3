LZW3
====

Compressor and decompressor that uses [LZW Algorithm](https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Welch) written in Python3.

## REQUIREMENTS

Requires at least Python 3.5.

## INSTALLATION

```
pip install lzw3
```

## USAGE

Two scripts will be installed in your local binary path (e.g. `/home/user/.local/bin`): `compress` and `uncompress`.
If you want to invoke these scripts, ensure that your `$PATH` contains the python binary path
Note that this compressor just compress regular files (i.e. doesn't create an archive such as .zip or .tar.gz).
Anyhow, directory can still be compressed using the option: `-r`

### Compression

The compression phases replaces the original files with the compressed ones, appending the extension ".Z"

Compress a list of files
```
compress doc1.txt doc2.txt
```
        
Compress a directory recursively
```
compress -r /home/user/Docs/Project
```

#### Options

```
    -r
        Recursively compress the files inside the directories
        within the given file list.
        If not specified, directories in the file list are skipped.

    -v
        Prints information about the handled files and the percentage of
        saved space for each compressed file.

    -t
        Prints the time spent for compress each file.

    -k
        Keeps the original files instead of replace those with the
        compressed ones.

    -d
        Prints debug messages.
```


### Decompression

The decompression phases replaces the compressed files (with extension ".Z") with the uncompressed ones.

Decompress a list of files
```
uncompress doc1.txt.Z doc2.txt.Z
```
        
Decompress a directory recursively
```
uncompress -r /home/user/Docs/Project
```

#### Options

```
    -r
        Recursively decompress the files inside the directories
        within the given file list.
        If not specified, directories in the file list are skipped.

    -v
        Prints information about the handled files.

    -t
        Prints the time spent for decompress each file.

    -k
        Keeps the decompressed files after the decompression.

    -d
        Prints debug messages.
```