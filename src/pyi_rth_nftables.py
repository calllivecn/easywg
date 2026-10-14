
import sys
# import os
import subprocess

from pathlib import Path


from log import (
    logger,
    DEBUG,
)


if getattr(sys, 'frozen', False):

    py_check = True

    for python in ("python", "python3"):
        try:
            p = subprocess.run([python, "-c", "import nftables;print(nftables.__file__)"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            py_check = False
            continue

        break


    if py_check:

        result = p.stdout.decode()
        external_lib_dir = Path(result).parent.parent
        if external_lib_dir not in sys.path:
            sys.path.append(str(external_lib_dir))

    # else:
    #     logger.warning("在当前系统上没有检测到 nftables py包, VPN模式依赖项。需要安装(ubuntu: apt install python3-nftables) 其他发行布问下AI。")
