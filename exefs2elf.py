# convert exefs to elf
import sys
import os
import struct

CC = "arm-none-eabi-gcc"
CP = "arm-none-eabi-g++"
OC = "arm-none-eabi-objcopy" 
LD = "arm-none-eabi-ld"
	
def run(cmd):
	os.system(cmd)

def writefile(path, s):
	with open(path, "wb") as f:
		f.write(str(s))

with open("workdir/exh.bin", "rb") as f:
	exh = f.read(64)

(textBase, textPages, roPages, rwPages, bssSize) = struct.unpack('16x ii 12x i 12x i 4x i', exh)
textSize = textPages * 0x1000
roSize   = roPages * 0x1000
rwSize   = rwPages * 0x1000
bssSize  = (int(bssSize / 0x1000) + 1) * 0x1000

print("textBase: {:08x}".format(textBase))
print("textSize: {:08x}".format(textSize))
print("roSize:   {:08x}".format(roSize))
print("rwSize:   {:08x}".format(rwSize))
print("bssSize:  {:08x}".format(bssSize))

if (textBase != 0x100000):
	print('WARNING: textBase mismatch, might be an encrypted exheader file.')

exefsPath = 'workdir/exefs/'
with open(exefsPath + 'code.bin', "rb") as f:
	text = f.read(textSize)
	ro = f.read(roSize)
	rw = f.read(rwSize)
	
with open('e2elf.ld', 'r') as f:
	ldscript = f.read()
ldscript = ldscript.replace('%memorigin%', str(textBase))
ldscript = ldscript.replace('%bsssize%', str(bssSize))
writefile('workdir/e2elf.ld', ldscript)

writefile(exefsPath + 'text.bin', text)
writefile(exefsPath + 'ro.bin', ro)
writefile(exefsPath + 'rw.bin', rw)

objfiles = ''
for i in (('text', 'text'), ('ro', 'rodata'), ('rw', 'data')):
	desc, sec_name = i
	run('{0} -I binary -O elf32-littlearm --rename-section .data=.{1} {2}{3}.bin {2}{3}.o'
        .format(OC, sec_name, exefsPath, desc))
	objfiles += '{0}{1}.o '.format(exefsPath, desc)
	
run(LD + ' --accept-unknown-input-arch -T workdir/e2elf.ld -o workdir/exefs.elf ' + objfiles)