# Heisenware-Native-Agent-Packager
This project provides utility tools to create various packages and installers for Heisenware Native Agents

## Features
 * Generates `.deb` packages with:
    * Daemon service that:
        * Has it's own working directory in `/var/lib/heisenware/{SERVICE_NAME}`
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
    * Checks if chosen installation path is not in disk root or blacklisted folders
    * Installs a windows service that:
        * Has it's own working directory in `${INSTDIR}`
        * Starts automatically on system startup
        * Starts automatically after installation
        * Restarts 10s after failure
        * Logs `StdOut` and `StdErr` to `${INSTDIR}/logs/service.log`
            * Take note, `service.log` is not rotated, or overridden on service restart
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
 * python >3.9 - used to execute package generation scripts
 * [dpkg](https://tracker.debian.org/pkg/dpkg) - used to build .deb packages (not necessary, if you don't plan to build dpkg packages)
 * [rpm](https://tracker.debian.org/pkg/rpm) - used to build .rpm packages (not necessary, if you don't plan to build rpm packages)
 * [NSIS](https://nsis.sourceforge.io/Main_Page) - Nullsoft Scriptable Install System, used to create windows installer wizard (not necessary, if you don't plan to build windows installers)

To install all of the above mentioned requirements on a debian based system, please use the following commands:

```bash
sudo apt install dpkg nsis python3 unzip wget rpm -y
```

## Optional requirements
 * sphinx - python documentation generator

To install sphinx on a debian based system, please use the following commands:

```bash
sudo apt-get install python3-sphinx python3-sphinx-rtd-theme -y
```

This project provides an HTML based documentation using sphinx and read the docs theme. To generate a local copy, please run the following: 

```bash
cd docs
make html
```

or if you are developing on windows

```bash
cd docs
make.bat html
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

## Tested on
Package generation has been manually tested with appropriate `test_inputs` files on the following systems:
 * debian trixie
 * debian bullseye
 * ubuntu 24.04

Generated package usage (installation, update and removal) has been manually tested on the following systems: 
 * amd64 debian trixie
 * arm64 debian trixie (Raspberry Pi 4B+)
 * arm64 debian trixie (Raspberry Pi 5)
 * amd64 ubuntu 24.04
 * amd64 fedora 43
 * amd64 windows 11 Enterprise Version 24H2 Build 26100.7171
 * amd64 Windows 10 Enterprise LTSC Version 21H2 Build 19044.6575

## Project structure

* `.vscode` - shared VSCode configuration files
* `docs` - sphinx documentation files
* `shared` - static files that are used by all packages/installers during creation 
* `dpkg` - static and template files that are required for `.deb` package creation
* `rpm` - static and template files that are required for `.rpm` package creation
* `nsis` - template files that are required by NSIS for Windows installer wizard creation
* `modules` - internal Python modules that are responsible for chosen package/installer creation
* `test_inputs` - stores test inputs for `package_native_agent.py`, only used during development
