import shutil
import subprocess
from pathlib import Path
from datetime import date
import modules.utils as utils

MAX_SYNOPSIS_LEN = 80


class __DpkgPackager(utils.Packager):
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
        self.control_dir = self.package_dir / 'DEBIAN'

    def setup_workplace(self):
        template_dir = self.cwd / 'dpkg'
        if not template_dir.is_dir():
            raise FileNotFoundError(f'Directory {template_dir} does not exist')

        utils.make_clean_dir(self.control_dir)

        shutil.copytree(src=template_dir, dst=self.control_dir,
                        dirs_exist_ok=True)
        self.control_dir.chmod(0o755)

    def add_binary(self, binary: Path):
        install_dir = self.package_dir / 'usr' / 'bin'
        utils.make_clean_dir(install_dir)

        binary_path = self.cwd / binary
        shutil.copy(src=binary_path, dst=install_dir)
        installed_binary = install_dir / binary.name
        installed_binary.chmod(0o755)

    def update_control(self):
        control_file = self.control_dir / 'control'
        content = utils.read_file_content(control_file)

        content = content.replace('{NAME}', self.package_name)
        content = content.replace('{VERSION}', self.version)
        content = content.replace('{ARCH}', self.arch)

        synopsis = utils.read_file_content(self.synopsis_file)
        if len(synopsis) > MAX_SYNOPSIS_LEN:
            raise RuntimeError('Package synopsis is too long')
        content = content.replace('{SYNOPSIS}', synopsis)

        description = utils.read_file_content(self.description_file)
        content = content.replace('{DESCRIPTION}', description)

        utils.write_file_content(control_file, content)

    def update_copyright(self):
        copyright_file = self.control_dir / 'copyright'
        content = content = utils.read_file_content(copyright_file)

        this_year = date.today().year
        content = content.replace('{YEAR}', f'{this_year}')

        license_text = utils.read_file_content(self.license_file)
        content = content.replace('{LICENSE_TEXT}', license_text)

        utils.write_file_content(copyright_file, content, mode=0o644)
        copyright_install_dir = self.package_dir / \
            'usr' / 'share' / 'doc' / self.package_name
        utils.make_clean_dir(copyright_install_dir)
        shutil.move(src=copyright_file, dst=copyright_install_dir)

    def update_daemon(self):
        daemon_template = self.control_dir / 'daemon.service'
        daemon_service = self.control_dir / f'{self.package_name}.service'
        daemon_template.rename(daemon_service)

        content = utils.read_file_content(daemon_service)

        synopsis = utils.read_file_content(self.synopsis_file)
        description = utils.read_file_content(self.description_file)
        full_description = f'{synopsis} {description}'
        content = content.replace('{DESCRIPTION}', full_description)
        content = content.replace(
            '{HEISENWARE_AGENT_BINARY}', self.binary_name)
        content = content.replace(
            '{NAME}', self.package_name)

        utils.write_file_content(daemon_service, content, mode=0o644)

        daemon_install_dir = self.package_dir / 'usr' / 'lib' / 'systemd' / 'system'
        utils.make_clean_dir(daemon_install_dir)
        shutil.move(src=daemon_service, dst=daemon_install_dir)

    def update_conffiles(self):
        config_file = self.control_dir / 'conffiles'
        content = utils.read_file_content(config_file)
        content = content.replace(
            '{NAME}', self.package_name)
        utils.write_file_content(config_file, content, mode=0o644)

    def add_logrotate(self):
        config_file = self.control_dir / 'logrotate.conf'

        content = utils.read_file_content(config_file)
        content = content.replace(
            '{NAME}', self.package_name)
        utils.write_file_content(config_file, content, mode=0o644)

        config_file = config_file.rename(self.control_dir / f'{self.package_name}.conf')
        config_install_dir = self.package_dir / 'etc' / 'logrotate.d'
        utils.make_clean_dir(config_install_dir)
        shutil.move(src=config_file, dst=config_install_dir)

    def update_scripts(self):
        preinst_file = self.control_dir / 'preinst'
        utils.update_script(preinst_file, self.package_name)

        postinst_file = self.control_dir / 'postinst'
        utils.update_script(postinst_file, self.package_name)

        prerm_file = self.control_dir / 'prerm'
        utils.update_script(prerm_file, self.package_name)

        postrm_file = self.control_dir / 'postrm'
        utils.update_script(postrm_file, self.package_name)

    def build(self):
        dpkg_found = subprocess.run(
            ['dpkg-deb', '--version'], capture_output=True, check=False)
        if dpkg_found.returncode != 0:
            raise FileNotFoundError('dpkg-deb not found')

        archive_name = f'{self.package_name}_{self.version}_{self.arch}'
        subprocess.run(
            ['dpkg-deb', '--build', '--root-owner-group', archive_name],
            cwd=self.package_dir.parent,
            check=True
        )
        shutil.rmtree(self.package_dir)

    def document(self):
        readme = self.package_dir.parent / 'README'
        content = 'Run the following command to install the package:\n' + \
            f'  sudo dpkg -i {self.package_name}_{self.version}_{self.arch}.deb\n' + \
            'If you need to uninstall the package, run the following:\n' + \
            f'  sudo dpkg -P {self.package_name}\n' + \
            '\n' + \
            'If you received `Error: logrotate is not installed` during installation,\n' + \
            'please ensure that logrotate package is installed on your system.\n' + \
            'On Debian-based systems you can do that by running the following command:\n' + \
            '   sudor apt install logrotate -y\n' 
        utils.write_file_content(readme, content)


def make(work_dir: Path, output_dir: Path, name: str, binary_path: Path, version: str, arch: str):
    packager = __DpkgPackager(work_dir, output_dir, name,
                              binary_path, version, arch)
    packager.setup_workplace()
    packager.add_binary(binary_path)
    packager.update_conffiles()
    packager.add_logrotate()
    packager.update_control()
    packager.update_copyright()
    packager.update_daemon()
    packager.update_scripts()
    packager.build()
    packager.document()
