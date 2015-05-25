#!/bin/sh -e

WD=$( pwd )
DIR=$( cd "$( dirname "$0" )" && pwd )

invalid_file() {
	echo "ERROR: input file is invalid"
	exit 1
}

if ! [ -r "$1" ]; then
	invalid_file
fi

mkdir -p "$DIR/workdir"
ctrtool --exefsdir="$DIR/workdir/exefs"   "$1" &>/dev/null || invalid_file
ctrtool --exheader="$DIR/workdir/exh.bin" "$1" &>/dev/null || invalid_file
( cd "$DIR" && python exefs2elf.py )
mv "$DIR/workdir/exefs.elf" "$WD"
rm -rf "$DIR/workdir"
