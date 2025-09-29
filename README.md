## ctr-elf-python3
#### Fork of [archshift's ctr-elf](https://github.com/archshift/ctr-elf) to work on Python 3, alongside some other changes to make it more in line with modern python standards and conventions.

Make sure to have the `arm-none-eabi-binutils` and `arm-none-eabi-gcc` dependencies installed before running!

Run with `python exefs2elf.py [exefs directory] [exheader file]` with `[exefs directory]` being the path of the exefs folder and `[exheader file]` the path of the exheader file, both without square brackets.

The output will be on `output/exefs.elf`.

