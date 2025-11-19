# Changelog
## [0.3.0] - 2025.11.19
### Fixed
 - Windows installer not removing `INSTDIR`
 - `package_native_agent.py` not expanding `~` to user directory in 
 `--input_file` and `--output_dir` arguments
 - Windows installer not setting expected space requirement

### Removed
 - NSIS Simple Service Plugin

### Changed
 - `shared/general/LICENSE` to hold correct license information
 - `shared/general/description` static file to hold updated description
 - `shared/linux/daemon.service` to create and use a custom work directory
 - `test_inputs/linux_test` script to create `.hw-agent-id` and 
 `.hw-cache/cacheFile1` to simulate heisenware native agent creating files 
 inside it's work directory
 - `package_native_agent.py` to check if `nssm.exe` exists in input directory
 when `--target_system=Amd64_Windows`
 - `modules/nsis.py` to copy `nssm.exe` into package directory
 - `nsis/installer.nsi` to use `nssm.exe` for service management
 - `nsis/installer.nsi` to check for invalid installation path 
 - `test_inputs/windows_test.exe` into `test_inputs/windows_test.bat` that creates
 `.hw-agent-id` and `.hw-cache/cacheFile1` files to simulate heisenware native 
 agent creating files inside it's work directory
 - `postrm` scripts for dpkg and rpm to remove `/var/lib/heisenware/{SERVICE_NAME}` 
 directory on purge
 - `postrm` scripts for dpkg and rpm to remove `/var/lib/heisenware` directory on 
 purge if there are no more services installed

### Added
 - `nssm.exe` to `test_inputs`
 - `hw-banner.bmp` to `nsis`
 - attribution to NSSM creator in `NOTICE` file
 - Finish pages to windows (un)installer 

## [0.2.0] - 2025.11.03
### Fixed
 - Daemon service not being enabled for Ubuntu systems
 - unicode detection for nsis on older debian machines
 - relative paths not being handled for `--input_file` and `--output` args

### Changed
 - `dpkg/postinst` maintainer script to use `systemctl enable` instead of 
`deb-systemd-helper enable` to fix daemon service enablement on Ubuntu machines
 - first windows service restart delay to 10s and second restart to 1 minute
 - `general` directory to `shared/general`
 - `tests` into `test_inputs` to clarify the purpose of stored files
 - `Packager` class to `PackagerArgs`
 - `__DpkgPackager` class to use `PackagerArgs` instead of `Packager` inheritance
 - `__NsisPackager` class to use `PackagerArgs` instead of `Packager` inheritance
 - `package_native_agent.py` to pass `PackagerArgs` as an argument to various 
`*.make()` calls
 - `Test:Linux` configuration to `Test: Amd64 Debian` in `.vscode/launch.json` 

### Added 
 - `Build-Depends: debhelper, dh-systemd` to `dpkg/control` file
 - `Depends: systemd` to `dpkg/control` file
 - `nsis/hw-logo.ico` as (un)installer icon
 - `shared/linux` directory to store shared daemon and config files
 - `rpm/package_name.spec` RPM spec file template
 - `__RpmPackager` class to handle RPM package creation
 - `Amd64_Fedora` option for `--target_system` arg
 - `Arm64_Fedora` option for `--target_system` arg 
 - `Test: Arm64 Debian"` configuration to `.vscode/launch.json`
 - `Test: Amd64 Fedora` configuration to `.vscode/launch.json`
 - `Test: Arm64 Fedora` configuration to `.vscode/launch.json`
 - `Tested on` section to `Readme.md`

## [0.1.0] - 2025.10.14
### Added
 - `genecis/LICENSE` file with placeholder text for commercial license
 - `genecis/synopsis` file with placeholder single line description text
 - `genecis/description` file with placeholder expanded description text
 - `dpkg/control` template file with `logrotate` dependency
 - `dpkg/copyright` template file with commercial and Apache v2 licensed files
 - `dpkg/conffiles` with `logrotate` config location
 - `dpkg/logrotate.conf` configuration to rotate at maximum 10 files, each with 
 max size of 20 MB
 - `dpkg` template maintainer scripts to handle daemon service start/stop/restart 
 policies and update mechanism
 - `nsis/installer.nsi` template file to specify Windows installer wizard generation
 - `tests/linux_test` shell script file for test runs during Linux package development
 - `tests/openssl/dummy_data` file to simulate openssl installation directory for 
 Windows installer development
 - `tests/windows_test.exe` service executable file for test runs during Windows 
 installer development
 - `modules/utils.py` to store shared functions and `Packager` class between all 
 internal modules
 - `modules/dpkg.py` to store `dpkg` specific generator functions
 - `modules/nsis.py` to store `nsis` specific generator functions
 - `.vscode/launch.json` configuration file with `Test: Linux` and `Test: Windows` 
 launch configurations for Visual Studio Code
 - `package_native_agent.py` to parse user input and call correct internal modules
