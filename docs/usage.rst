=================
Usage
=================

This script uses `argparse <https://docs.python.org/3/library/argparse.html>`__ to specify, parse and verify user input arguments. 
Call `package_native_agent.py --help` to get a list of required arguments and their descriptions.

.. code-block:: bash

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

Example usage: 

.. code-block:: bash

    ./package_native_agent.py --input_file input_binary --target_system Amd64_Debian --agent_id abcd --account_name Test --workspace_name Default --version 00-1
