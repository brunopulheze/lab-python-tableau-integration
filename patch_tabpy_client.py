#!/usr/bin/env python3
"""
patch_tabpy_client.py

Backs up tabpy_client/rest.py and replaces 'from collections import MutableMapping'
with 'from collections.abc import MutableMapping' to support Python 3.10+.

Usage:
  (activate your .venv)
  python patch_tabpy_client.py
"""
import sys
import os
import shutil

try:
    import tabpy_client.rest as rest_mod
    rest_path = rest_mod.__file__
except Exception as e:
    print("Error: cannot locate tabpy_client.rest module. Is tabpy-client installed in this env?")
    print("Exception:", e)
    sys.exit(1)

print("Located tabpy_client.rest at:", rest_path)

backup_path = rest_path + ".bak"
if not os.path.exists(backup_path):
    shutil.copy2(rest_path, backup_path)
    print("Backup created at:", backup_path)
else:
    print("Backup already exists at:", backup_path)

# Read file
with open(rest_path, "r", encoding="utf-8") as f:
    src = f.read()

old_line = "from collections import MutableMapping as _MutableMapping"
new_line = "from collections.abc import MutableMapping as _MutableMapping"

if old_line in src:
    src2 = src.replace(old_line, new_line)
    with open(rest_path, "w", encoding="utf-8") as f:
        f.write(src2)
    print("Patched tabpy_client.rest successfully.")
    # print a small excerpt to confirm
    start = src2.find(new_line)
    print("Context around change:\n", src2[start:start+200])
    print("Now test import with: python -c \"from tabpy_client.client import Client; print('OK')\"")
else:
    print("No matching import line found in file. The file may already be patched or different.")
    # try to find other occurrences
    if "MutableMapping" in src:
        idx = src.find("MutableMapping")
        print("Found 'MutableMapping' at index", idx, "showing surrounding text:")
        print(src[max(0, idx-80): idx+80])
    else:
        print("No 'MutableMapping' usage found. Nothing changed.")