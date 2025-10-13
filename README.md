# Heisenware-Native-Agent-Packager
This project provides utility tools to create various packages and installers for Heisenware Native Agents

## Requirements
 * python >3.7 - used to execute package generation scripts
 * [dpkg](https://tracker.debian.org/pkg/dpkg) - used to build .deb packages (not necessary, if you don't plan to build dpkg packages)
 * [NSIS](https://nsis.sourceforge.io/Main_Page) - Nullsoft Scriptable Install System, used to create windows installer wizard (not necessary, if you don't plan to build windows installers)
    * [NSIS Simple Service Plugin](https://nsis.sourceforge.io/NSIS_Simple_Service_Plugin) - use to generate windows service installation scripts
    * [AccessControl plug-in](https://nsis.sourceforge.io/AccessControl_plug-in) - use to modify installed directory permissions

To install all of the above mentioned requirements, please use the following commands:

```bash
sudo apt install dpkg nsis python3 unzip wget -y
wget -O NSIS_Simple_Service.zip https://nsis.sourceforge.io/mediawiki/images/e/ef/NSIS_Simple_Service_Plugin_Unicode_1.30.zip
unzip -d nsis_service NSIS_Simple_Service.zip && rm NSIS_Simple_Service.zip
sudo mv nsis_service/SimpleSC.dll /usr/share/nsis/Plugins/x86-unicode/ && rm -rf nsis_service
```

## Usage

This script uses [`argparse`](https://docs.python.org/3/library/argparse.html) to specify, parse and verify user input arguments. Call `package_native_agent.py --help` to get a list of required arguments and their descriptions.

```
package_native_agent.py
    -h, --help            show this help message and exit
    --input_file INPUT_FILE
                          Path to the packaged Heisenware native agent binary file binary file
    --output_dir OUTPUT_DIR
                          Generated package/installer output directory (defaults to current work directory) binary file
    --target_system {Amd64_Debian,Arm64_Debian,Amd64_Windows}
                          Target package platform and architecture
    --agent_id AGENT_ID   Generated Heisenware native agent id
    --account_name ACCOUNT_NAME
                          Heisenware Platform account name
    --workspace_name WORKSPACE_NAME
                          Heisenware Platform workspace name
    --version VERSION     Heisenware Platform version number
```

Example usage: 

```bash
./package_native_agent.py --input_file input_binary --target_system Amd64_Debian --agent_id abcd --account_name Test --workspace_name Default --version 00-1
```

## Project structure

* `.vscode` - shared VSCode configuration files
* `generic` - static files that are used by all packages/installers during creation 
* `dpkg` - static and template files that are required for `.deb` package creation
* `nsis` - template files that are required by NSIS for Windows installer wizard creation
* `modules` - internal Python modules that are responsible for chosen package/installer creation
* `tests` - stores test inputs for `package_native_agent.py`, only used during development
