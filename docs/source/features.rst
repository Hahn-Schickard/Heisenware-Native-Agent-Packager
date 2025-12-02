=================
Features
=================
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