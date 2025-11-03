from pathlib import Path
import shutil
import os


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


class PackagerArgs:
    def __init__(self,
                 packager_dir: Path,
                 output_dir: Path,
                 name: str,
                 binary_path: Path,
                 version: str,
                 arch: str
                 ):
        self.packager_dir = packager_dir
        self.shared_dir = self.packager_dir / 'shared'
        self.synopsis_file = self.shared_dir / 'general' / 'synopsis'
        self.description_file = self.shared_dir / 'general' / 'description'
        self.license_file = self.shared_dir / 'general' / 'LICENSE'

        self.cwd = os.getcwd()
        if not binary_path.is_absolute():
            self.binary_path = self.cwd / binary_path
        else:
            self.binary_path = binary_path
        self.binary_name = Path(self.binary_path).name

        self.package_name = name
        self.version = version
        self.arch = arch
        self.tmp_dir = f'{self.package_name}_{self.version}_{self.arch}'
        if not output_dir.is_absolute():
            self.output_dir = self.cwd / output_dir / self.tmp_dir
        else:
            self.output_dir = output_dir / self.tmp_dir
