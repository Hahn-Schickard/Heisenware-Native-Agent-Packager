#!/usr/bin/env python3

import argparse
from pathlib import Path
import modules.dpkg as dpkg


if __name__ == '__main__':
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
            'Arm64_Debian'
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
    args = parser.parse_args()

    package_name = f'heisenware-{args.agent_id}-{args.account_name}-{args.workspace_name}'
    this_dir = Path(Path(__file__).absolute()).parent

    dpkg.make(this_dir, args.output_dir, package_name, Path(args.input_file), args.version, args.target_system)
