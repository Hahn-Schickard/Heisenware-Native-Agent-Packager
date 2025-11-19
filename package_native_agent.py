#!/usr/bin/env python3

import argparse
import sys
import traceback
from pathlib import Path
from modules.utils import PackagerArgs
import modules.dpkg as dpkg
import modules.rpm as rpm
import modules.nsis as nsis


def make_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--input_file',
        help='Path to the packaged Heisenware native agent binary file'
        ' binary file',
        type=str,
        required=True
    )
    parser.add_argument(
        '--output_dir',
        help='Generated package/installer output directory (defaults to current work directory)'
        ' binary file',
        type=str,
        default=''
    )
    parser.add_argument(
        '--target_system',
        help='Target package platform and architecture',
        choices=[
            'Amd64_Debian',
            'Arm64_Debian',
            'Amd64_Fedora',
            'Arm64_Fedora',
            'Amd64_Windows'
        ],
        required=True
    )
    parser.add_argument(
        '--agent_id',
        help='Generated Heisenware native agent id',
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

    input_file = Path(args.input_file).expanduser()
    if not input_file.is_file():
        print(f'Given input file {input_file} does not exist', file=sys.stderr)
        sys.exit(1)

    arch = args.target_system
    arch = arch.lower()
    arch_sanitized = arch.replace('_debian', '').replace(
        '_fedora', '').replace('_windows', '')
    packager = PackagerArgs(this_dir,
                            Path(args.output_dir).expanduser(),
                            package_name,
                            input_file,
                            args.version,
                            arch_sanitized)

    try:
        if arch.endswith('_debian'):
            dpkg.make(packager)
        elif arch.endswith('_fedora'):
            rpm.make(packager)
        elif arch.endswith('_windows'):
            openssl_dir = input_file.parent / 'openssl'
            if not openssl_dir.is_dir():
                print(f'Expected Openssl directory in {openssl_dir},'
                      ' but it does not exists', file=sys.stderr)
                sys.exit(1)
            
            nssm_binary = input_file.parent / 'nssm.exe'
            if not nssm_binary.exists():
                print(f'Expected NSSM executable in {openssl_dir},'
                      ' but it does not exists', file=sys.stderr)
                sys.exit(1)
            nsis.make(packager)
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(1)
