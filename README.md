
## ctr-elf
#### Creates an ELF from a 3DS executable EXEFS

Make sure to have both the `arm-none-eabi-binutils` and `arm-none-eabi-gcc` dependencies installed before running!

Run with `python exefs2elf.py [exefs directory] [exheader file]` with `[exefs directory]` being the path of the exefs folder and `[exheader file]` the path of the exheader file.

The output will be on `output/exefs.elf`.

#### Forked from [44670's patchrom](https://github.com/44670/patchrom)
