import shutil
import subprocess
from datetime import date
import modules.utils as utils

MAX_SYNOPSIS_LEN = 80


class __DpkgPackager():
    def __init__(self,
                 args: utils.PackagerArgs):
        self.args = args
        self.control_dir = self.args.output_dir / 'DEBIAN'

    def setup_workplace(self):
        template_dir = self.args.packager_dir / 'dpkg'
        if not template_dir.is_dir():
            raise FileNotFoundError(f'Directory {template_dir} does not exist')

        utils.make_clean_dir(self.control_dir)

        shutil.copytree(src=template_dir, dst=self.control_dir,
                        dirs_exist_ok=True)

        shared_linux_dir = self.args.shared_dir / 'linux'
        shutil.copytree(src=shared_linux_dir, dst=self.control_dir,
                        dirs_exist_ok=True)

        self.control_dir.chmod(0o755)

    def add_binary(self):
        install_dir = self.args.output_dir / 'usr' / 'bin'
        utils.make_clean_dir(install_dir)

        shutil.copy(src=self.args.binary_path, dst=install_dir)
        installed_binary = install_dir / self.args.binary_name
        installed_binary.chmod(0o755)

    def update_control(self):
        control_file = self.control_dir / 'control'
        content = utils.read_file_content(control_file)

        content = content.replace('{NAME}', self.args.package_name)
        content = content.replace('{VERSION}', self.args.version)
        content = content.replace('{ARCH}', self.args.arch)

        synopsis = utils.read_file_content(self.args.synopsis_file)
        if len(synopsis) > MAX_SYNOPSIS_LEN:
            raise RuntimeError('Package synopsis is too long')
        content = content.replace('{SYNOPSIS}', synopsis)

        description = utils.read_file_content(self.args.description_file)
        content = content.replace('{DESCRIPTION}', description)

        utils.write_file_content(control_file, content)

    def update_copyright(self):
        copyright_file = self.control_dir / 'copyright'
        content = content = utils.read_file_content(copyright_file)

        this_year = date.today().year
        content = content.replace('{YEAR}', f'{this_year}')

        license_text = utils.read_file_content(self.args.license_file)
        content = content.replace('{LICENSE_TEXT}', license_text)

        utils.write_file_content(copyright_file, content, mode=0o644)
        copyright_install_dir = self.args.output_dir / \
            'usr' / 'share' / 'doc' / self.args.package_name
        utils.make_clean_dir(copyright_install_dir)
        shutil.move(src=copyright_file, dst=copyright_install_dir)

    def update_daemon(self):
        daemon_template = self.control_dir / 'daemon.service'
        daemon_service = self.control_dir / f'{self.args.package_name}.service'
        daemon_template.rename(daemon_service)

        content = utils.read_file_content(daemon_service)

        synopsis = utils.read_file_content(self.args.synopsis_file)
        description = utils.read_file_content(self.args.description_file)
        full_description = f'{synopsis} {description}'
        content = content.replace('{DESCRIPTION}', full_description)
        content = content.replace(
            '{HEISENWARE_AGENT_BINARY}', self.args.binary_name)
        content = content.replace(
            '{NAME}', self.args.package_name)

        utils.write_file_content(daemon_service, content, mode=0o644)

        daemon_install_dir = self.args.output_dir / 'usr' / 'lib' / 'systemd' / 'system'
        utils.make_clean_dir(daemon_install_dir)
        shutil.move(src=daemon_service, dst=daemon_install_dir)

    def update_conffiles(self):
        config_file = self.control_dir / 'conffiles'
        content = utils.read_file_content(config_file)
        content = content.replace(
            '{NAME}', self.args.package_name)
        utils.write_file_content(config_file, content, mode=0o644)

    def add_logrotate(self):
        config_file = self.control_dir / 'logrotate.conf'

        content = utils.read_file_content(config_file)
        content = content.replace(
            '{NAME}', self.args.package_name)
        utils.write_file_content(config_file, content, mode=0o644)

        config_file = config_file.rename(
            self.control_dir / f'{self.args.package_name}.conf')
        config_install_dir = self.args.output_dir / 'etc' / 'logrotate.d'
        utils.make_clean_dir(config_install_dir)
        shutil.move(src=config_file, dst=config_install_dir)

    def update_scripts(self):
        preinst_file = self.control_dir / 'preinst'
        utils.update_script(preinst_file, self.args.package_name)

        postinst_file = self.control_dir / 'postinst'
        utils.update_script(postinst_file, self.args.package_name)

        prerm_file = self.control_dir / 'prerm'
        utils.update_script(prerm_file, self.args.package_name)

        postrm_file = self.control_dir / 'postrm'
        utils.update_script(postrm_file, self.args.package_name)

    def build(self):
        dpkg_found = subprocess.run(
            ['dpkg-deb', '--version'], capture_output=True, check=False)
        if dpkg_found.returncode != 0:
            raise FileNotFoundError('dpkg-deb not found')

        archive_name = self.args.tmp_dir
        subprocess.run(
            ['dpkg-deb', '--build', '--root-owner-group', archive_name],
            cwd=self.args.output_dir.parent,
            check=True
        )
        shutil.rmtree(self.args.output_dir)

    def document(self):
        readme = self.args.output_dir.parent / 'README'
        content = 'Run the following command to install the package:\n' + \
            f'  sudo dpkg -i {self.args.package_name}_{self.args.version}_{self.args.arch}.deb\n' + \
            'If you need to uninstall the package, run the following:\n' + \
            f'  sudo dpkg -P {self.args.package_name}\n' + \
            '\n' + \
            'If you received `Error: logrotate is not installed` during installation,\n' + \
            'please ensure that logrotate package is installed on your system.\n' + \
            'On Debian-based systems you can do that by running the following command:\n' + \
            '   sudo apt install logrotate -y\n'
        utils.write_file_content(readme, content)


def make(args: utils.PackagerArgs):
    packager = __DpkgPackager(args)
    packager.setup_workplace()
    packager.add_binary()
    packager.update_conffiles()
    packager.add_logrotate()
    packager.update_control()
    packager.update_copyright()
    packager.update_daemon()
    packager.update_scripts()
    packager.build()
    packager.document()
