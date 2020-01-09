""" Registree and committee email helper functions
"""

from db import DB

import pyperclip


def get_registree_emails():
    dbh = DB()
    emails = list(set([r.email for r in dbh.get_all_registrees() if r.email]))
    emails.sort()
    return emails


def copy_registree_email_list(debug=False):
    """ kwds accepted to allow sub process argparse handling with minimal extra code
    """

    emails = "; ".join(get_registree_emails())
    if debug:
        print("Registree emails:", emails)
    pyperclip.copy(emails)
    print("Registree emails copied to clipboard")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "-v", "--verbose", action="store_true", dest="debug", help="Enable debug output"
    )
    subparsers = parser.add_subparsers(help="sub-commands")
    parser_registree_emails = subparsers.add_parser(
        "registree_emails", help="copy all registree emails to clipboard"
    )
    parser_registree_emails.set_defaults(func=copy_registree_email_list)
    args = parser.parse_args()
    args_dict = {}
    for k in vars(args):
        if k not in ('func',):
            args_dict[k] = getattr(args, k)
    args.func(args_dict)
