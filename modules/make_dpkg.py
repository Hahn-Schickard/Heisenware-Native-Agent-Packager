import shutil
import subprocess
import sys
import os
from datetime import date

MAX_SYNOPSIS_LEN = 80

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
    content = __read_file_content(control_file)

    content.replace(r'{NAME}', package_name)
    content.replace(r'{VERSION}', version)
    content.replace(r'{ARCH}', arch)

    synopsis_file = os.path.join(os.getcwd(), '..', 'generic', 'synopsis')
    synopsis = __read_file_content(synopsis_file)
    if len(synopsis) > MAX_SYNOPSIS_LEN:
        raise RuntimeError('Package synopsis is too long')
    content.replace(r'{SYNOPSIS}', synopsis)

    description_file = os.path.join(os.getcwd(), '..', 'generic', 'description')
    description = __read_file_content(description_file)
    content.replace(r'{DESCRIPTION}', description)

    __write_file_content(control_file, content)

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
    daemon_template = os.path.join(os.getcwd(), 'DEBIAN', 'heisenware.service')
    daemon_service = os.path.join(os.getcwd(), 'DEBIAN', f'heisenware-{package_name}.service')
    os.rename(src=daemon_template, dst=daemon_service)
    
    content = __read_file_content(daemon_service)

    synopsis_file = os.path.join(os.getcwd(), '..', 'generic', 'synopsis')
    synopsis = __read_file_content(synopsis_file)
    description_file = os.path.join(os.getcwd(), '..', 'generic', 'description')
    description = __read_file_content(description_file)
    full_description = synopsis + description
    content.replace(r'{DESCRIPTION}', full_description)

    content.replace(r'{HEISENWARE_AGENT_BINARY}', binary_name)

def __update_script(script_file:str, service_name:str):
    content = __read_file_content(script_file)
    content.replace(r'{SERVICE_NAME}', service_name)
    __write_file_content(script_file, content)

def __update_scripts(package_name:str):
    service_name = f'heisenware-{package_name}'
    
    preinst_file = os.path.join(os.getcwd(), 'DEBIAN', 'preinst')
    __update_script(preinst_file, service_name)

    postinst_file = os.path.join(os.getcwd(), 'DEBIAN', 'postinst')
    __update_script(postinst_file, service_name)

    prerm_file = os.path.join(os.getcwd(), 'DEBIAN', 'prerm')
    __update_script(prerm_file, service_name)

    postrm_file = os.path.join(os.getcwd(), 'DEBIAN', 'postrm')
    __update_script(postrm_file, service_name)

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
