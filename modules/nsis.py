"""NSIS Installer Generator Module for Heisenware Windows Native Agents"""

import shutil
import subprocess
import modules.utils as utils


class __NsisPackager():
    """NSIS Installer Builder Class
    """

    def __init__(self,
                 args: utils.PackagerArgs):
        self.args = args
        self.required_space = 0

    def setup_workplace(self):
        """Setup a temporary workplace for NSIS installer creation

         The workplace will be created in 
            [OUTPUT_DIR]/[PACKAGE_NAME]_[VERSION]_[ARCH]

        The created workplace directory will contain shared windows general
        as well as NSIS template files

        Sets correct directory and file permissions

        Raises:
            FileNotFoundError: if template files or output dir does not exist
        """
        template_dir = self.args.packager_dir / 'nsis'
        if not template_dir.is_dir():
            raise FileNotFoundError(f'Directory {template_dir} does not exist')

        utils.make_clean_dir(self.args.output_dir)

        shutil.copytree(src=template_dir, dst=self.args.output_dir,
                        dirs_exist_ok=True)
        self.args.output_dir.chmod(0o755)

    def add_binary(self):
        """Copy the Heisenware Native Agent, NSSM binary and openssl folder into the installer

        Set the correct permissions for the binary and openssl folder

        Calculate the total required space in KB and save it in a class variable
        """
        shutil.copy(src=self.args.binary_path, dst=self.args.output_dir)
        installed_binary = self.args.output_dir / self.args.binary_name
        installed_binary.chmod(0o755)
        self.required_space = installed_binary.stat().st_size

        shutil.copy(src=self.args.binary_path.parent / 'nssm.exe',
                    dst=self.args.output_dir)
        installed_nssm_binary = self.args.output_dir / 'nssm.exe'
        installed_nssm_binary.chmod(0o755)
        self.required_space = self.required_space + installed_nssm_binary.stat().st_size

        openssl_dir = self.args.binary_path.parent / 'openssl'
        installed_openssl = self.args.output_dir / 'openssl'
        shutil.copytree(src=openssl_dir, dst=installed_openssl,
                        dirs_exist_ok=True)
        installed_openssl.chmod(0o755)
        self.required_space = self.required_space + \
            utils.get_directory_size(installed_openssl)
        self.required_space = self.required_space / 1024  # convert to KB

    def add_license(self):
        """Update the license content
        """
        shutil.copy(src=self.args.license_file, dst=self.args.output_dir)

    def update_installer(self):
        """Update the NSIS installer script with package meta information

        Uses NSIS escape option to avoid NSIS special chars

        Writes the calculated space requirement so the installer wizard 
        can show estimated space requirement
        """
        installer_file = self.args.output_dir / 'installer.nsi'
        content = utils.read_file_content(installer_file)

        content = content.replace('{NAME}', self.args.package_name)
        content = content.replace('{VERSION}', self.args.version)

        synopsis = utils.read_file_content(self.args.synopsis_file)
        content = content.replace('{SYNOPSIS}', synopsis)

        description = utils.read_file_content(self.args.description_file)
        content = content.replace('{DESCRIPTION}', description)

        content = content.replace(
            '{HEISENWARE_AGENT_BINARY}', self.args.binary_name)

        content = content.replace(
            '{REQUIRED_SPACE}', str(round(self.required_space)))

        utils.write_file_content(installer_file, content, nsis_escape=True)

    def build(self):
        """Call the makensis to build windows installer

        Remove the temporary workplace directory after successful build

        Raises:
            FileNotFoundError: if makensis does not exists
        """
        nsis_found = subprocess.run(
            ['makensis', '-VERSION'], capture_output=True, check=False)
        if nsis_found.returncode != 0:
            raise FileNotFoundError('makensis not found')

        nsis_file = self.args.output_dir / 'installer.nsi'
        subprocess.run(
            ['makensis', '-v2', nsis_file],
            cwd=self.args.output_dir,
            check=True
        )
        shutil.rmtree(self.args.output_dir)


def make(args: utils.PackagerArgs):
    """Create a windows installer wizard

    Args:
        args (utils.PackagerArgs): Input arguments for the builder class
    """
    packager = __NsisPackager(args)
    packager.setup_workplace()
    packager.add_binary()
    packager.add_license()
    packager.update_installer()
    packager.build()
