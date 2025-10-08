import shutil
import subprocess
from pathlib import Path
from datetime import date

MAX_SYNOPSIS_LEN = 80


def make_clean_dir(path: Path, mode=0o755):
    if path.is_dir():
        shutil.rmtree(path)

    # create each parent on it's own, to ensure correct dir permissions
    # if we use path.mkdir(parents=True), the dir permissions will be
    # set to 0777 instead of 0755 with no way of changing it later
    for parent in reversed(path.parents):
        if not parent.exists():
            parent.mkdir(mode)
    path.mkdir(mode)


def read_file_content(path: Path):
    if not path.exists():
        raise FileNotFoundError(f'File {path} does not exist')

    with open(file=path, mode='r', encoding='utf-8') as file:
        content = file.read()

    return content


def write_file_content(path: Path, content: str, mode=0o744):
    with open(file=path, mode='w', encoding='utf-8') as file:
        file.write(content)
    path.chmod(mode)

def update_script(script_file: Path, service_name: str):
    content = read_file_content(script_file)
    content = content.replace('{SERVICE_NAME}', service_name)
    write_file_content(script_file, content, mode=0o755)


class __Packager:
    def __init__(self,
                 work_dir: Path,
                 output_dir: Path,
                 name: str,
                 binary_path: Path,
                 version: str,
                 arch: str
                 ):
        self.cwd = work_dir
        self.package_name = name
        self.binary_path = binary_path
        self.version = version
        self.arch = arch
        self.binary_name = Path(self.binary_path).name
        self.package_dir = self.cwd / output_dir / \
            f'{self.package_name}_{self.version}_{self.arch}'
        self.control_dir = self.package_dir / 'DEBIAN'
        self.synopsis_file = self.cwd / 'generic' / 'synopsis'
        self.description_file = self.cwd / 'generic' / 'description'
        self.license_file = self.cwd / 'generic' / 'LICENSE'

    def setup_workplace(self):
        template_dir = self.cwd / 'dpkg'
        if not template_dir.is_dir():
            raise FileNotFoundError(f'Directory {template_dir} does not exist')

        make_clean_dir(self.control_dir)

        shutil.copytree(src=template_dir, dst=self.control_dir,
                        dirs_exist_ok=True)
        self.control_dir.chmod(0o755)

    def update_control(self):
        control_file = self.control_dir / 'control'
        content = read_file_content(control_file)

        content = content.replace('{NAME}', self.package_name)
        content = content.replace('{VERSION}', self.version)
        content = content.replace('{ARCH}', self.arch)

        synopsis = read_file_content(self.synopsis_file)
        if len(synopsis) > MAX_SYNOPSIS_LEN:
            raise RuntimeError('Package synopsis is too long')
        content = content.replace('{SYNOPSIS}', synopsis)

        description = read_file_content(self.description_file)
        content = content.replace('{DESCRIPTION}', description)

        write_file_content(control_file, content)

    def update_copyright(self):
        copyright_file = self.control_dir / 'copyright'
        content = content = read_file_content(copyright_file)

        this_year = date.today().year
        content = content.replace('{YEAR}', f'{this_year}')

        license_text = read_file_content(self.license_file)
        content = content.replace('{LICENSE_TEXT}', license_text)

        write_file_content(copyright_file, content, mode=0o644)
        copyright_install_dir = self.package_dir / \
            'usr' / 'share' / 'doc' / self.package_name
        make_clean_dir(copyright_install_dir)
        shutil.move(src=copyright_file, dst=copyright_install_dir)

    def update_daemon(self):
        daemon_template = self.control_dir / 'daemon.service'
        daemon_service = self.control_dir / f'{self.package_name}.service'
        daemon_template.rename(daemon_service)

        content = read_file_content(daemon_service)

        synopsis = read_file_content(self.synopsis_file)
        description = read_file_content(self.description_file)
        full_description = f'{synopsis} {description}'
        content = content.replace('{DESCRIPTION}', full_description)
        content = content.replace(
            '{HEISENWARE_AGENT_BINARY}', self.binary_name)

        write_file_content(daemon_service, content, mode=0o644)

        daemon_install_dir = self.package_dir / 'usr' / 'lib' / 'systemd' / 'system'
        make_clean_dir(daemon_install_dir)
        shutil.move(src=daemon_service, dst=daemon_install_dir)

    def update_scripts(self):
        preinst_file = self.control_dir / 'preinst'
        update_script(preinst_file, self.package_name)

        postinst_file = self.control_dir / 'postinst'
        update_script(postinst_file, self.package_name)

        prerm_file = self.control_dir / 'prerm'
        update_script(prerm_file, self.package_name)

        postrm_file = self.control_dir / 'postrm'
        update_script(postrm_file, self.package_name)

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
            f'  sudo dpkg -P {self.package_name}\n'
        write_file_content(readme, content)


def make(work_dir: Path, output_dir: Path, name: str, binary_path: Path, version: str, arch: str):
    arch = arch.replace('_Debian', '')
    arch = arch.lower()
    packager = __Packager(work_dir, output_dir, name,
                          binary_path, version, arch)
    packager.setup_workplace()

    full_binary_path = work_dir / binary_path
    install_dir = packager.package_dir / 'usr' / 'bin'
    make_clean_dir(install_dir)
    shutil.copy(src=full_binary_path, dst=install_dir)

    packager.update_control()
    packager.update_copyright()
    packager.update_daemon()
    packager.update_scripts()
    packager.build()
    packager.document()
