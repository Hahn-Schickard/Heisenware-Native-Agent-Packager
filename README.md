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
sudo apt install dpkg nsis python3 unzip -y
wget -O NSIS_Simple_Service.zip https://nsis.sourceforge.io/mediawiki/images/e/ef/NSIS_Simple_Service_Plugin_Unicode_1.30.zip
wget -O NSIS_Access_Control.zip https://nsis.sourceforge.io/mediawiki/images/4/4a/AccessControl.zip
unzip -d nsis_service NSIS_Simple_Service.zip && rm NSIS_Simple_Service.zip
unzip -d nsis_access_control NSIS_Access_Control.zip && rm NSIS_Access_Control.zip
sudo mv nsis_service/*.dll /usr/share/nsis/Plugins/ && rm -rf nsis_service
sudo mv nsis_access_control/Plugins/amd64-unicode/AccessControl.dll /usr/share/nsis/Plugins/x86-unicode && rm -rf nsis_access_control
```
