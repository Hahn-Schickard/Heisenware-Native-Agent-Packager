from pathlib import Path
import shutil

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
