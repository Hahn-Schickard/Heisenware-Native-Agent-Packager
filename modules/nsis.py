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
        self.installer_dir = self.package_dir

    def setup_workplace(self):
        template_dir = self.cwd / 'nsis'
        if not template_dir.is_dir():
            raise FileNotFoundError(f'Directory {template_dir} does not exist')

        utils.make_clean_dir(self.installer_dir)

        shutil.copytree(src=template_dir, dst=self.installer_dir,
                        dirs_exist_ok=True)
        self.installer_dir.chmod(0o755)

    def add_binary(self, binary: Path):
        binary_path = self.cwd / binary
        shutil.copy(src=binary_path, dst=self.installer_dir)
        installed_binary = self.installer_dir / binary.name
        installed_binary.chmod(0o755)

        openssl_dir = binary.parent / 'openssl'
        installed_openssl = self.installer_dir / 'openssl'
        shutil.copytree(src=openssl_dir, dst=installed_openssl,
                        dirs_exist_ok=True)
        installed_openssl.chmod(0o755)

    def add_license(self):
        shutil.copy(src=self.license_file, dst=self.installer_dir)

    def update_installer(self):
        installer_file = self.installer_dir / 'installer.nsi'
        content = utils.read_file_content(installer_file)

        content = content.replace('{NAME}', self.package_name)
        content = content.replace('{VERSION}', self.version)

        synopsis = utils.read_file_content(self.synopsis_file)
        content = content.replace('{SYNOPSIS}', synopsis)

        description = utils.read_file_content(self.description_file)
        content = content.replace('{DESCRIPTION}', description)

        content = content.replace(
            '{HEISENWARE_AGENT_BINARY}', self.binary_name)

        utils.write_file_content(installer_file, content)

    def build(self):
        nsis_found = subprocess.run(
            ['makensis', '-VERSION'], capture_output=True, check=False)
        if nsis_found.returncode != 0:
            raise FileNotFoundError('makensis not found')

        nsis_file = self.installer_dir / 'installer.nsi'
        subprocess.run(
            ['makensis', '-v2', nsis_file],
            cwd=self.installer_dir,
            check=True
        )
        shutil.rmtree(self.installer_dir)


def make(work_dir: Path, output_dir: Path, name: str, binary_path: Path, version: str, arch: str):
    packager = __NsisPackager(work_dir, output_dir, name, binary_path, version, arch)
    packager.setup_workplace()
    packager.add_binary(binary_path)
    packager.add_license()
    packager.update_installer()
    packager.build()
