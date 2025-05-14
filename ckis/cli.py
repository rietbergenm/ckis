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


    parser_prune = subparsers.add_parser("prune", help = "prune old artifacts")

    parser_prune.add_argument(
        "-c",
        "--chain",
        type = str,
        action = "append",
        help = "prune only runs for the specified chains"
    )
    parser_prune.add_argument(
        "-k",
        "--kver",
        type = str,
        help = ("prune all runs for this kernel version")
    )

    return parser.parse_args()
