# Heisenware-Native-Agent-Packager
This project provides utility tools to create various packages and installers for Heisenware Native Agents

## Features
 * Generates `.deb` packages with:
    * Daemon service that:
        * Starts automatically on system startup
        * Restarts 5s after service failure
        * Saves called service binary output in `journal`
        * Saves called service binary output in `/var/log/heisenware/` directory as logfiles
    * Logrotate configuration that:
        * Limits maximum logfile size to 20 MB 
        * Rotates the logs over 10 backup files once the size limit is reached
    * Maintainer scripts that: 
        * Checks if daemon service is already installed
        * (Un)Install the daemon service
        * Creates `/var/log/heisenware/` directory if it does not exist
    * Support for **Amd64** and **Arm64** architectures
 * Generated `.rpm` packages with: 
    * Same features as `.deb` packages
 * Generates Windows installer wizards that:
    * Checks if a previous installation exists
    * Allows the user to select the install location
    * Installs a windows service that:
        * Starts automatically on system startup
        * Restarts a minute after failure
        * Restarts 5 minutes after the first restart attempt failure
    * Creates an uninstaller that:
        * Checks if a service is running and asks for user consent to stop it, before continuing
        * Removes installed service
        * Removes Windows registry values for the installation
        * Removes installed files
    * Defines Windows registry values for:
        * Program install location
        * Installed version
        * Uninstaller location
    * Supports **Amd64** architecture for installed binaries (generated installer uses **x86** architecture)

## Requirements
 * python >3.7 - used to execute package generation scripts
 * [dpkg](https://tracker.debian.org/pkg/dpkg) - used to build .deb packages (not necessary, if you don't plan to build dpkg packages)
 * [NSIS](https://nsis.sourceforge.io/Main_Page) - Nullsoft Scriptable Install System, used to create windows installer wizard (not necessary, if you don't plan to build windows installers)
    * [NSIS Simple Service Plugin](https://nsis.sourceforge.io/NSIS_Simple_Service_Plugin) - use to generate windows service installation scripts

To install all of the above mentioned requirements, please use the following commands:

```bash
sudo apt install dpkg nsis python3 unzip wget rpm -y
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
* `shared` - static files that are used by all packages/installers during creation 
* `dpkg` - static and template files that are required for `.deb` package creation
* `rpm` - static and template files that are required for `.rpm` package creation
* `nsis` - template files that are required by NSIS for Windows installer wizard creation
* `modules` - internal Python modules that are responsible for chosen package/installer creation
* `test_inputs` - stores test inputs for `package_native_agent.py`, only used during development
