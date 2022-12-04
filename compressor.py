import lz
import huffman
import sys

i = 1
failed = False

if len(sys.argv) == 1 or ((len(sys.argv)-1) % 3 != 0):
    print("[COMPRESS/DECOMPRESS] INPUT FILE OUTPUT FILE")
    print("[-c compress] [-d decompress]\n")
    failed = True

while i < len(sys.argv) - 2 and failed is False:
    arg = sys.argv[i]
    i += 1
    arg2 = sys.argv[i]
    i += 1
    arg3 = sys.argv[i]
    i+=1
    match arg:
        case "-c":
            print("compressing...")
            lz.compress(arg2, arg3)
            huffman.compress(arg3, arg3)
            print("done.")
        case "-d":
            print("decompressing...")
            huffman.decompress(arg2, arg3)
            lz.decompress(arg3, arg3)
            print("done.")
        case _:
            print("Invalid arguments.")
            print("[-c compress] [-d decompress] ")

