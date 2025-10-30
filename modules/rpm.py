import shutil
import subprocess
from pathlib import Path
from datetime import date
import modules.utils as utils


class __RpmPackager(utils.Packager):
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
        if self.arch == 'amd64':
            self.arch = 'x86_64'
        elif self.arch == 'arm64':
            self.arch = 'aarch64-linux'

        self.version = self.version.replace('-', '.')
        self.spec_file = self.package_dir / f'{self.package_name}.spec'

    def setup_workplace(self):
        template_dir = self.cwd / 'rpm'
        if not template_dir.is_dir():
            raise FileNotFoundError(f'Directory {template_dir} does not exist')

        utils.make_clean_dir(self.package_dir)

        shutil.copytree(src=template_dir, dst=self.package_dir,
                        dirs_exist_ok=True)

        shared_linux_dir = self.shared_dir / 'linux'
        shutil.copytree(src=shared_linux_dir, dst=self.package_dir,
                        dirs_exist_ok=True)

        self.package_dir.chmod(0o755)

    def add_binary(self, binary: Path):
        binary_path = self.cwd / binary
        shutil.copy(src=binary_path, dst=self.package_dir)

    def update_specfile(self):
        spec_file_template = self.package_dir / 'package_name.spec'
        spec_file_template.rename(self.spec_file)

        content = utils.read_file_content(self.spec_file)

        synopsis = utils.read_file_content(self.synopsis_file)
        description = utils.read_file_content(self.description_file)
        content = content.replace('{SYNOPSIS}', synopsis)
        content = content.replace('{DESCRIPTION}', description)
        content = content.replace(
            '{OUTPUT_DIR}', str(self.package_dir.absolute()))
        content = content.replace(
            '{HEISENWARE_AGENT_BINARY}', self.binary_name)
        content = content.replace('{VERSION}', self.version)
        content = content.replace('{NAME}', self.package_name)
        timestamp = date.today().strftime('%a %b %d %Y')
        content = content.replace('{DATE}', timestamp)

        utils.write_file_content(self.spec_file, content, mode=0o644)

    def update_daemon(self):
        daemon_template = self.package_dir / 'daemon.service'
        daemon_service = self.package_dir / f'{self.package_name}.service'
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

    def add_logrotate(self):
        config_file = self.package_dir / 'logrotate.conf'

        content = utils.read_file_content(config_file)
        content = content.replace(
            '{NAME}', self.package_name)
        utils.write_file_content(config_file, content, mode=0o644)

        config_file = config_file.rename(
            self.package_dir / f'{self.package_name}')

    def add_license(self):
        license_file = self.package_dir / 'LICENSE'
        shutil.copy(src=self.license_file, dst=license_file)
        license_file.chmod(0o644)

    def build(self):
        rpm_found = subprocess.run(
            ['rpmbuild', '--version'], capture_output=True, check=False)
        if rpm_found.returncode != 0:
            raise FileNotFoundError('makensis not found')

        subprocess.run(
            ['rpmbuild',
             f'--target={self.arch}',
             f'{self.spec_file}',
             '-bb',
             '--build-in-place',
             '--nodebuginfo'
             ],
            cwd=self.package_dir,
            check=True
        )
        #rpmbuild --target expects aarch64-linux, but builds with aarch64 postfix
        self.arch = self.arch.replace('-linux','')
        rpm_package_name = f'{self.package_name}-{self.version}-1.{self.arch}.rpm'
        rmp_file = self.package_dir / self.arch / rpm_package_name
        shutil.move(src=rmp_file, dst=self.package_dir.parent)
        shutil.rmtree(self.package_dir)

    def document(self):
        readme = self.package_dir.parent / 'README'
        content = 'Run the following command to install the package:\n' + \
            f'  sudo dnf localinstall {self.package_name}_{self.version}_{self.arch}.rpm\n' + \
            'If you need to uninstall the package, run the following:\n' + \
            f'  sudo dnf remove {self.package_name}\n' + \
            '\n' + \
            'If you received `Error: logrotate is not installed` during installation,\n' + \
            'please ensure that logrotate package is installed on your system.\n' + \
            'On Fedora-based systems you can do that by running the following command:\n' + \
            '   sudo dnf install logrotate -y\n'
        utils.write_file_content(readme, content)


def make(work_dir: Path, output_dir: Path, name: str, binary_path: Path, version: str, arch: str):
    packager = __RpmPackager(work_dir, output_dir, name,
                             binary_path, version, arch)
    packager.setup_workplace()
    packager.add_binary(binary_path)
    packager.update_specfile()
    packager.update_daemon()
    packager.add_logrotate()
    packager.add_license()
    packager.build()
    packager.document()
