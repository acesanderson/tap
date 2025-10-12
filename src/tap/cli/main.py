from tap.cli.parser import create_parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    from tap.cli.router import route_command

    route_command(args)
