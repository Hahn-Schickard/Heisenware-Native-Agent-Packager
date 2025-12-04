=================
Requirements
=================

This script is written in python 3 and is intended to be used in a debian based linux distribution, virtual machine or a docker image. 
The script uses external third-party tools to generate the desired packages. Please ensure that the following is installed:

 * python >3.9 - used to execute package generation scripts
 * `dpkg <https://tracker.debian.org/pkg/dpkg>`__  - used to build .deb packages (not necessary, if you don't plan to build dpkg packages)
 * `rpm <https://tracker.debian.org/pkg/rpm>`__ - used to build .rpm packages (not necessary, if you don't plan to build rpm packages)
 * `NSIS <https://nsis.sourceforge.io/Main_Page>`__  - Nullsoft Scriptable Install System, used to create windows installer wizard (not necessary, if you don't plan to build windows installers)

To install all of the above mentioned requirements on a debian based system, please use the following commands:

.. code-block:: bash

    sudo apt install dpkg nsis python3 unzip wget rpm -y
