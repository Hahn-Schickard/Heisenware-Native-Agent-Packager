import shutil
import subprocess
from pathlib import Path
import modules.utils as utils

class __NsisPackager(utils.Packager):
    def __init__(self,
                 work_dir: Path,
                 output_dir: Path,
                 name: str,
                 binary_path: Path,
                 version: str,
                 arch: str
                 ):
        utils.Packager.__init__(
            self,
            work_dir,
            output_dir,
            name,
            binary_path,
            version, arch
        )

def make(work_dir: Path, output_dir: Path, name: str, binary_path: Path, version: str, arch: str):
    packager = __NsisPackager(work_dir, output_dir, name,
                              binary_path, version, arch)
    print('Ran NSIS packager')