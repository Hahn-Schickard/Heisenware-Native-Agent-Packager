import shutil
import subprocess
import modules.utils as utils


class __NsisPackager():
    def __init__(self,
                 args: utils.PackagerArgs):
        self.args = args

    def setup_workplace(self):
        template_dir = self.args.packager_dir / 'nsis'
        if not template_dir.is_dir():
            raise FileNotFoundError(f'Directory {template_dir} does not exist')

        utils.make_clean_dir(self.args.output_dir)

        shutil.copytree(src=template_dir, dst=self.args.output_dir,
                        dirs_exist_ok=True)
        self.args.output_dir.chmod(0o755)

    def add_binary(self):
        shutil.copy(src=self.args.binary_path, dst=self.args.output_dir)
        installed_binary = self.args.output_dir / self.args.binary_name
        installed_binary.chmod(0o755)

        shutil.copy(src=self.args.binary_path.parent / 'nssm.exe',
                    dst=self.args.output_dir)
        installed_nssm_binary = self.args.output_dir / 'nssm.exe'
        installed_nssm_binary.chmod(0o755)

        openssl_dir = self.args.binary_path.parent / 'openssl'
        installed_openssl = self.args.output_dir / 'openssl'
        shutil.copytree(src=openssl_dir, dst=installed_openssl,
                        dirs_exist_ok=True)
        installed_openssl.chmod(0o755)

    def add_license(self):
        shutil.copy(src=self.args.license_file, dst=self.args.output_dir)

    def update_installer(self):
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

        utils.write_file_content(installer_file, content, nsis_escape=True)

    def build(self):
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
    packager = __NsisPackager(args)
    packager.setup_workplace()
    packager.add_binary()
    packager.add_license()
    packager.update_installer()
    packager.build()
