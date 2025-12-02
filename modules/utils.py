"""Utility module for other packager modules"""

from pathlib import Path
import shutil
import os


def make_clean_dir(path: Path, mode=0o755):
    """Create a new directory in a given path

    If directory already exists, deletes original content

    Args:
        path (Path): path to output directory
        mode (octal, optional): directory permissions. Defaults to 0o755.
    """
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
    """Read given file content

    Args:
        path (Path): path to input file

    Raises:
        FileNotFoundError: if given file does not exist

    Returns:
        string: untrimmed file content
    """
    if not path.exists():
        raise FileNotFoundError(f'File {path} does not exist')

    with open(file=path, mode='r', encoding='utf-8') as file:
        content = file.read()

    return content


def write_file_content(path: Path, content: str, mode=0o744, nsis_escape=False):
    """Write given content to a given file

    Args:
        path (Path): path to output file
        content (str): content to write
        mode (octal, optional): file permissions. Defaults to 0o744.
        nsis_escape (bool, optional): adds NSIS escape chars. Defaults to False.
    """
    if nsis_escape:
        content = content.replace(r'\'', r'$\'')
    with open(file=path, mode='w', encoding='utf-8') as file:
        file.write(content)
    path.chmod(mode)


def update_script(script_file: Path, service_name: str):
    """Update a given script file with a given service name

    Args:
        script_file (Path): path to the maintainer script
        service_name (str): service name that will replace {SERVICE_NAME} placeholders
    """
    content = read_file_content(script_file)
    content = content.replace('{SERVICE_NAME}', service_name)
    write_file_content(script_file, content, mode=0o755)


def get_directory_size(directory: Path):
    """Calculate given directory size in bytes

    Args:
        directory (Path): target directory

    Returns:
        int: directory size in bytes
    """
    size = 0
    for f in directory.rglob('*'):
        if f.is_file():
            size += f.stat().st_size
    return size


class PackagerArgs:
    """Package information arguments and paths to shared template files
    """

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
