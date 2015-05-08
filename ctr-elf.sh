#!/bin/bash

WD=$( pwd )
DIR=$( cd "$( dirname '$0' )" && pwd )

invalid_file() {
	echo "ERROR: input file is invalid"
	exit 1
}

mkdir -p $DIR/workdir
ctrtool --exefsdir=$DIR/workdir/exefs   "$1" &>/dev/null || invalid_file
ctrtool --exheader=$DIR/workdir/exh.bin "$1" &>/dev/null || invalid_file
python $DIR/exefs2elf.py
mv $DIR/workdir/exefs.elf $WD
rm -rf $DIR/workdir
