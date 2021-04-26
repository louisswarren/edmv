# edmv
Move (rename) files using your text editor

Usage:

    edmv
    edmv SOURCES

With no argument, uses all files in the current working directory as `SOURCES`.

Opens your `EDITOR` on a temporary file listing all of the paths in `SOURCES`.
If your editor exits normally, moves the source files to the new paths
specified in the file.

Any newlines occuring in filenames are translated to `'\0'` in the temporary
file (as this is not a valid character in file paths).
