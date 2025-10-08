import shutil
import subprocess
import sys
import os
from datetime import date

def __make_clean_dir(dir_path:str):
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)
    os.mkdir(dir_path)

def __setup_workplace(workplace_dir:str, package_name:str):
    template_dir = os.path.join(workplace_dir, 'dpkg')
    if not os.path.isdir(template_dir):
        raise FileNotFoundError(f'Directory {template_dir} does not exist')
    
    package_dir = os.path.join(workplace_dir, package_name)
    __make_clean_dir(package_dir)
    control_dir = os.path.join(package_dir, 'DEBIAN')

    shutil.copytree(src=template_dir, dst=control_dir)
    os.chdir(package_dir)

def __read_file_content(file_path:str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'File {file_path} does not exist')
    
    with open(file=file_path, mode='r', encoding='utf-8') as file:
        content = file.read()

    return content

def __write_file_content(file_path:str, content: str):
    with open(file=file_path, mode='w', encoding='utf-8') as file:
        file.write(content)

def __update_control(package_name:str, version:str, arch:str):
    control_file = os.path.join(os.getcwd(), 'DEBIAN', 'control')
    control = __read_file_content(control_file)

    control.replace(r'{NAME}', package_name)
    control.replace(r'{VERSION}', version)
    control.replace(r'{ARCH}', arch)

    synopsis_file = os.path.join(os.getcwd(), '..', 'generic', 'synopsis')
    synopsis = __read_file_content(synopsis_file)
    if len(synopsis) > 80:
        raise RuntimeError('Package synopsis is too long')
    control.replace(r'{SYNOPSIS}', synopsis)

    description_file = os.path.join(os.getcwd(), '..', 'generic', 'description')
    description = __read_file_content(description_file)
    control.replace(r'{DESCRIPTION}', description)

    __write_file_content(control_file, control)

def __update_copytright():
    copyright_file = os.path.join(os.getcwd(), 'DEBIAN', 'copyright')
    content = __read_file_content(copyright_file)

    this_year = date.today().year
    content.replace(r'{YEAR}', this_year)

    license_file = os.path.join(os.getcwd(), '..', 'generic', 'LICENSE')
    license_text = __read_file_content(license_file)
    content.replace(r'{LICENSE_TEXT}', license_text)

    __write_file_content(copyright_file, content)


def __update_daemon(package_name:str, binary_name:str):
    # rename daemon template to heisenware_{packag_name}.service
    # set daemon Descrtiption from general/synopis + description files
    # change {HEISENWARE_AGENT_BINARY} placeholder to {binary_name}
    pass

def __update_scripts(package_name:str):
    # change {SERVICE_NAME} in preinst, postinst, prerm and postrm scripts to {package_name}
    pass

def __build_dpkg():
    # check if dpkg-deb exists $(dpkg-deb --version) == 0
    # dpkg-deb --build ${PACKAGE_NAME}_${VERSION}
    pass

def make_dpkg(cwd:str, package_name:str, binary_name:str, version:str, arch:str):
    __setup_workplace(cwd, package_name)

    binary_path = os.path.join(cwd, binary_name)
    install_dir = os.path.join(os.getcwd(), 'usr', 'bin')
    __make_clean_dir(install_dir)
    install_path = os.path.join(install_dir, binary_name)
    shutil.move(src=binary_path, dst=install_path)

    __update_control(package_name, version, arch)
    __update_copytright()
    __update_daemon(package_name, binary_name)
    __update_scripts(package_name)
    __build_dpkg()
    os.chdir(cwd)
