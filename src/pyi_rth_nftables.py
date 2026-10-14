
import sys
# import os
import subprocess

from pathlib import Path

if getattr(sys, 'frozen', False):

    try:
        p = subprocess.run(["python3", "-c", "import nftables;print(nftables.__file__)"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        p = subprocess.run(["python", "-c", "import nftables;print(nftables.__file__)"], check=True, capture_output=True)

    result = p.stdout.decode()

    external_lib_dir = Path(result).parent.parent
    # print(external_lib_dir)
    if external_lib_dir not in sys.path:
        # sys.path.insert(0, str(external_lib_dir))
        sys.path.append(str(external_lib_dir))
 
