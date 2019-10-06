import sys
import os
import argparse
from modfile import ModFile
from modfile_exceptions import ModFileException

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Terraria mod (.tmod) unpacker")
    parser.add_argument("file", help = "mod file path")
    args = parser.parse_args()

    mod = ModFile(args.file)
    
    try:
        print("[#] Please wait...")
        mod.unpack()
        print("[+] Unpacked successfully!")
        print("[+] TModLoader: {version} [{type}]".format(type = "OLD" if mod.minor_version < 11 else "NEW", version = mod.loader_version))
        print("[+] Mod name: " + mod.mod_name)
        print("[+] Mod version: " + mod.mod_version)
        print("[#] Unpacked files: " + str(mod.mod_files))

    except IOError:
        print("[-] Unable to read file " + args.file)

    except ModFileException as ex:
        print("[-] Unable to unpack mod: " + str(ex))