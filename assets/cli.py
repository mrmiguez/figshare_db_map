import os
import sys
import argparse

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def argument_parser():
    '''Top level argument parser'''
    args = argparse.ArgumentParser(description='Figshare data-mapping DB utility')
    args.add_argument('-s', '--status', help='get DB status', action='store_true')
    args.add_argument('-v', '--verbose', action='store_true')
    args.add_argument('-b', '--burndown', action='store_true', help='burndown database')
    run_args_group = args.add_argument_group('Run data mapping')
    run_args_group.add_argument('-r', '--run', action='store_true')
    run_args_group.add_argument('record_directory', help='path to XML records')

    # hack to show help when no arguments supplied
    if len(sys.argv) == 1:
        args.print_help()
        sys.exit(0)

    return args