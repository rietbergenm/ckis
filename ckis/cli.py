import argparse

def handle_options():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--config",
        metavar = "file",
        type = argparse.FileType(mode = 'rb'),
        help = "configuration file to use"
    )


    subparsers = parser.add_subparsers(
        title = "command",
        dest = "cmd",
        required = True,
        help = "the command to run"
    )


    parser_run = subparsers.add_parser("run", help = "run one or more chains")

    parser_run.add_argument(
        "kver",
        type = str,
        help = "kernel version to run chain for"
    )
    parser_run.add_argument(
        "-c",
        "--chain",
        type = str,
        action = "append",
        help = "run only the specified chains"
    )
    parser_run.add_argument(
        "-u",
        "--until",
        type = str,
        default = "",
        help = "run until the specified link (globbing is supported)"
    )
    
    return parser.parse_args()
