=================
Project structure
=================

* `.vscode` - shared VSCode configuration files
* `docs` - sphinx documentation files
* `shared` - static files that are used by all packages/installers during creation 
* `dpkg` - static and template files that are required for `.deb` package creation
* `rpm` - static and template files that are required for `.rpm` package creation
* `nsis` - template files that are required by NSIS for Windows installer wizard creation
* `modules` - internal Python modules that are responsible for chosen package/installer creation
* `test_inputs` - stores test inputs for `package_native_agent.py`, only used during development
