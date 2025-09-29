# convert exefs to elf
import os
import struct
import subprocess  # this works better on python3 than os.system()
import sys

CC = "arm-none-eabi-gcc"
CP = "arm-none-eabi-g++"
OC = "arm-none-eabi-objcopy"
LD = "arm-none-eabi-ld"


def run(cmd):
    return subprocess.run(cmd, shell=True, check=True)


def writefile(path, data):
    with open(path, "wb") as f:
        # Python 3 fix n1: Python 3 uses bytes for binary data, while Python 2
        #                  always uses strings. We must fix this behavior by
        #                  ensuring we always use bytes/byte arrays.
        if isinstance(data, str):
            f.write(data.encode("utf-8"))
        else:
            f.write(data)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            f"USAGE: python exefs2elf.py [exefs directory] [exheader file] with"
            + " [exefs directory] being the path of the exefs folder and"
            + " [exheader file] the path of the exheader file, both without square brackets."
        )
        sys.exit()

    if not os.path.exists(sys.argv[1]) or not os.path.exists(sys.argv[2]):
        print("ERROR: One or both of the paths given do not exist.")
        sys.exit()

    exefs_directory = sys.argv[1]
    exheader_file = sys.argv[2]

    with open(exheader_file, "rb") as f:
        exh = f.read(64)

    (text_base, text_pages, ro_pages, rw_pages, bss_size) = struct.unpack(
        "16x ii 12x i 12x i 4x i", exh
    )
    text_size = text_pages * 0x1000
    ro_size = ro_pages * 0x1000
    rw_size = rw_pages * 0x1000

    # Python 3 fix n2: Python 2 does integer divisions between integers,
    # 				   while Python 3 always does true divisions. We must
    # 				   adapt to this behavior by using //.
    bss_size = (int(bss_size // 0x1000) + 1) * 0x1000

    print("textBase: {:08x}".format(text_base))
    print("textSize: {:08x}".format(text_size))
    print("roSize:   {:08x}".format(ro_size))
    print("rwSize:   {:08x}".format(rw_size))
    print("bssSize:  {:08x}".format(bss_size))

    if text_base != 0x100000:
        print("WARNING: textBase mismatch, might be an encrypted exheader file.")

    code_bin_path = os.path.join(exefs_directory, "code.bin")
    if not os.path.exists(code_bin_path):
        print("ERROR: code.bin not present on the exefs directory.")
        sys.exit()

    with open(code_bin_path, "rb") as f:
        text = f.read(text_size)
        ro = f.read(ro_size)
        rw = f.read(rw_size)

    os.makedirs("output", exist_ok=True)

    with open(os.path.join(".", "e2elf.ld"), "r") as f:
        ld_script = f.read()
    ld_script = ld_script.replace("%memorigin%", str(text_base))
    ld_script = ld_script.replace("%bsssize%", str(bss_size))
    writefile(os.path.join("output", "e2elf.ld"), ld_script)

    writefile(os.path.join(exefs_directory, "text.bin"), text)
    writefile(os.path.join(exefs_directory, "ro.bin"), ro)
    writefile(os.path.join(exefs_directory, "rw.bin"), rw)

    obj_files = ""
    for i in (("text", "text"), ("ro", "rodata"), ("rw", "data")):
        desc, sec_name = i
        input_bin = os.path.join(exefs_directory, f"{desc}.bin")
        output_obj = os.path.join(exefs_directory, f"{desc}.o")

        run(
            f"{OC} -I binary -O elf32-littlearm --rename-section .data=.{sec_name} {input_bin} {output_obj}"
        )
        obj_files += output_obj + " "

    temp_ld_script_path = os.path.join("output", "e2elf.ld")
    exefs_elf = os.path.join("output", "exefs.elf")
    run(
        LD
        + f" --accept-unknown-input-arch -T {temp_ld_script_path} -o {exefs_elf} "
        + obj_files
    )

    # cleanup temporary e2elf.ld file
    if os.path.exists(temp_ld_script_path):
        os.remove(temp_ld_script_path)
