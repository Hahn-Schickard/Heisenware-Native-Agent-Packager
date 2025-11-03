import shutil
import subprocess
from datetime import date
import modules.utils as utils


class __RpmPackager():
    def __init__(self,
                 args: utils.PackagerArgs):
        self.args = args
        if self.args.arch == 'amd64':
            self.args.arch = 'x86_64'
        elif self.args.arch == 'arm64':
            self.args.arch = 'aarch64-linux'

        self.args.version = self.args.version.replace('-', '.')
        self.spec_file = self.args.output_dir / \
            f'{self.args.package_name}.spec'

    def setup_workplace(self):
        template_dir = self.args.packager_dir / 'rpm'
        if not template_dir.is_dir():
            raise FileNotFoundError(f'Directory {template_dir} does not exist')

        utils.make_clean_dir(self.args.output_dir)

        shutil.copytree(src=template_dir, dst=self.args.output_dir,
                        dirs_exist_ok=True)

        shared_linux_dir = self.args.shared_dir / 'linux'
        shutil.copytree(src=shared_linux_dir, dst=self.args.output_dir,
                        dirs_exist_ok=True)

        self.args.output_dir.chmod(0o755)

    def add_binary(self):
        shutil.copy(src=self.args.binary_path, dst=self.args.output_dir)

    def update_specfile(self):
        spec_file_template = self.args.output_dir / 'package_name.spec'
        spec_file_template.rename(self.spec_file)

        content = utils.read_file_content(self.spec_file)

        synopsis = utils.read_file_content(self.args.synopsis_file)
        description = utils.read_file_content(self.args.description_file)
        content = content.replace('{SYNOPSIS}', synopsis)
        content = content.replace('{DESCRIPTION}', description)
        content = content.replace(
            '{OUTPUT_DIR}', str(self.args.output_dir.absolute()))
        content = content.replace(
            '{HEISENWARE_AGENT_BINARY}', self.args.binary_name)
        content = content.replace('{VERSION}', self.args.version)
        content = content.replace('{NAME}', self.args.package_name)
        timestamp = date.today().strftime('%a %b %d %Y')
        content = content.replace('{DATE}', timestamp)

        utils.write_file_content(self.spec_file, content, mode=0o644)

    def update_daemon(self):
        daemon_template = self.args.output_dir / 'daemon.service'
        daemon_service = self.args.output_dir / \
            f'{self.args.package_name}.service'
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

    def add_logrotate(self):
        config_file = self.args.output_dir / 'logrotate.conf'

        content = utils.read_file_content(config_file)
        content = content.replace(
            '{NAME}', self.args.package_name)
        utils.write_file_content(config_file, content, mode=0o644)

        config_file = config_file.rename(
            self.args.output_dir / f'{self.args.package_name}')

    def add_license(self):
        shutil.copy(src=self.args.license_file, dst=self.args.output_dir)

    def build(self):
        rpm_found = subprocess.run(
            ['rpmbuild', '--version'], capture_output=True, check=False)
        if rpm_found.returncode != 0:
            raise FileNotFoundError('makensis not found')

        subprocess.run(
            ['rpmbuild',
             '--build-in-place',
             '--nodebuginfo',
             f'--target={self.args.arch}',
             f'{self.spec_file}',
             '-bb'             
             ],
            cwd=self.args.output_dir,
            check=True
        )
        # rpmbuild --target expects aarch64-linux, but builds with aarch64 postfix
        self.args.arch = self.args.arch.replace('-linux', '')
        rpm_package_name = f'{self.args.package_name}-{self.args.version}-1.{self.args.arch}.rpm'
        rmp_file = self.args.output_dir / self.args.arch / rpm_package_name
        shutil.move(src=rmp_file, dst=self.args.output_dir.parent)
        shutil.rmtree(self.args.output_dir)

    def document(self):
        readme = self.args.packager_dir.parent / 'README'
        content = 'Run the following command to install the package:\n' + \
            f'  sudo dnf localinstall {self.args.package_name}_{self.args.version}_{self.args.arch}.rpm\n' + \
            'If you need to uninstall the package, run the following:\n' + \
            f'  sudo dnf remove {self.args.package_name}\n' + \
            '\n' + \
            'If you received `Error: logrotate is not installed` during installation,\n' + \
            'please ensure that logrotate package is installed on your system.\n' + \
            'On Fedora-based systems you can do that by running the following command:\n' + \
            '   sudo dnf install logrotate -y\n'
        utils.write_file_content(readme, content)


def make(args: utils.PackagerArgs):
    packager = __RpmPackager(args)
    packager.setup_workplace()
    packager.add_binary()
    packager.update_specfile()
    packager.update_daemon()
    packager.add_logrotate()
    packager.add_license()
    packager.build()
    packager.document()
