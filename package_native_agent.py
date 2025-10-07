import argparse

def __check_args():
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--input_file',
        help='Path to the generated Heisenware native agent'
        ' binary file',
        type=str
    )
    parser.add_argument(
        '--target_system',
        help='Target package platform and architechture',
        choices=[
            'Amd64_Debian',
            'Arm64_Debian'
        ]
    )
    parser.add_argument(
        '--agent_id',
        help='Heisenware native agent id',
        type=str
    )
    parser.add_argument(
        '--account_name',
        help='Heisenware Platform account name',
        type=str
    )
    parser.add_argument(
        '--workspace_name',
        help='Heisenware Platform workspace name',
        type=str
    )
    parser.add_argument(
        '--version',
        help='Heisenware Platform version number',
        type=str
    )
