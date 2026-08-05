import argparse
import sys

from sort_table import sort_table
from check_table import check_table_consistency as check_table_links
from check_repo_link_vs_user_link_inconsistencies import check_table_consistency
from fix_serials import fix_serials


def cmd_sort(args):
    """Sort the README table by GitHub star count."""
    sort_table(args.file)


def cmd_check(args):
    """Run consistency checks on the README table."""
    file_path = args.file
    check_table_links(file_path)
    check_table_consistency(file_path)


def cmd_fix_serials(args):
    """Re-number table rows sequentially starting from 1."""
    fix_serials(args.file)
    print(f"Serial numbers fixed in {args.file}")


def cmd_all(args):
    """Run the full pipeline: sort → check → fix serials."""
    cmd_sort(args)
    cmd_fix_serials(args)
    cmd_check(args)



def main():
    parser = argparse.ArgumentParser(
        prog="top-ai-repos",
        description="Maintain the Top-AI-repos curated list.",
    )
    parser.add_argument(
        "-f", "--file",
        default="README.md",
        help="Path to the README file (default: README.md)",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("sort", help="Sort table by star count")
    subparsers.add_parser("check", help="Run consistency checks")
    subparsers.add_parser("fix-serials", help="Fix row serial numbers")
    subparsers.add_parser("all", help="Run full pipeline: sort, fix-serials, check")

    args = parser.parse_args()

    commands = {
        "sort": cmd_sort,
        "check": cmd_check,
        "fix-serials": cmd_fix_serials,
        "all": cmd_all,
    }

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands[args.command](args)


if __name__ == "__main__":
    main()
