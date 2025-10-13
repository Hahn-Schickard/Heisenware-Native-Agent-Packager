#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
import modules.dpkg as dpkg
import modules.nsis as nsis


def make_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--input_file',
        help='Path to the generated Heisenware native agent'
        ' binary file',
        type=str,
        required=True
    )
    parser.add_argument(
        '--output_dir',
        help='Path to the generated Heisenware native agent'
        ' binary file',
        type=str,
        default=''
    )
    parser.add_argument(
        '--target_system',
        help='Target package platform and architechture',
        choices=[
            'Amd64_Debian',
            'Arm64_Debian',
            'Amd64_Windows'
        ],
        required=True
    )
    parser.add_argument(
        '--agent_id',
        help='Heisenware native agent id',
        type=str,
        required=True
    )
    parser.add_argument(
        '--account_name',
        help='Heisenware Platform account name',
        type=str,
        required=True
    )
    parser.add_argument(
        '--workspace_name',
        help='Heisenware Platform workspace name',
        type=str,
        required=True
    )
    parser.add_argument(
        '--version',
        help='Heisenware Platform version number',
        type=str,
        required=True
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = make_args()
    package_name = f'heisenware-{args.agent_id}-{args.account_name}-{args.workspace_name}'
    this_dir = Path(Path(__file__).absolute()).parent
    
    input_file = Path(args.input_file)
    if not input_file.is_file():
        print(f'Given input file {input_file} does not exist', file=sys.stderr)
        sys.exit(1)

    arch = args.target_system
    arch = arch.lower()

    if arch.endswith('_debian'):
        arch = arch.replace('_debian', '')
        dpkg.make(this_dir,
                  args.output_dir,
                  package_name,
                  input_file,
                  args.version,
                  arch
                  )
    elif arch.endswith('_windows'):
        openssl_dir = input_file.parent / 'openssl'
        if not openssl_dir.is_dir():
            print(f'Expected Openssl directory in {openssl_dir},'
                  ' but it does not exists', file=sys.stderr)
            sys.exit(1)

        nsis.make(this_dir,
                  args.output_dir,
                  package_name,
                  input_file,
                  args.version,
                  arch
                  )
