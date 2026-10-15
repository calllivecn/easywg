
import sys
# import os
import subprocess

from pathlib import Path


from log import (
    logger,
    DEBUG,
)


if getattr(sys, 'frozen', False):

    py_version = False
    py = None

    for python in ("python", "python3"):
        # 先检测系统有没有python
        try:
            r = subprocess.run([python, "-V"], check=True, capture_output=True)
        except FileNotFoundError:
            continue

        if r.returncode == 0:
            py_version = True
            py = python
            break


    py_check = True
    p = None
    if py_version and py is not None:

        try:
            p = subprocess.run([py, "-c", "import nftables;print(nftables.__file__)"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            py_check = False


        if py_check and p is not None:

            result = p.stdout.decode()
            external_lib_dir = Path(result).parent.parent
            if external_lib_dir not in sys.path:
                sys.path.append(str(external_lib_dir))

        # else:
        #     logger.warning("在当前系统上没有检测到 nftables py包, VPN模式依赖项。需要安装(ubuntu: apt install python3-nftables) 其他发行布问下AI。")
