""" Registree and committee email helper functions
"""

from md410_2020_conv_common.db import DB

import pyperclip

import os, os.path

class Error(Exception):
    pass

def get_registree_emails(filter_attributes=[]):
    dbh = DB()
    fas = [('email', True)]
    for fa in filter_attributes:
        fas.append(fa)
    emails = list(set([r.email for r in dbh.get_all_registrees() if all([bool(getattr(r, a)) == v for (a,v) in fas])]))
    emails.sort()
    return emails

def get_registree_email_string(filter_attributes=[]):
    emails = "; ".join(get_registree_emails(filter_attributes=filter_attributes))
    return emails

def copy_registree_email_list(filter_attributes=[], debug=False):

    emails = get_registree_email_string(filter_attributes=filter_attributes)
    if debug:
        print("Registree emails:", emails)
    pyperclip.copy(emails)
    print("Registree emails copied to clipboard")


def send_email_to_registrees(text_file):
    try:
        with open(text_file, 'r') as fh:
            text = [l.strip() for l in fh]
    except Exception as e:
        raise
        raise Error(f'Specified text file "{text_file}" does not exist or cannot be opened')
    emails = get_registree_email_string()
    pyperclip.copy(emails)
    print(f"To: addresses copied to clipboard: {emails}")
    input()
    subj = text[0]
    pyperclip.copy(subj)
    print(f"Subject copied to clipboard: {subj}")
    input()
    body = '\n'.join(text[1:])
    pyperclip.copy(body)
    print("Body copied to clipboard:")
    print(body)
    input()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    subparsers = parser.add_subparsers(help="sub-commands")
    parser_registree_emails = subparsers.add_parser(
        "registree_emails", help="copy all registree emails to clipboard"
    )
    parser_registree_emails.add_argument(
        "-v", "--verbose", action="store_true", dest="debug", help="Enable debug output"
    )
    parser_registree_emails.add_argument(
         "-u", "--unpaid_only", action="store_true", help="Only provides email for people who have not paid in full"
    )
    parser_registree_emails.set_defaults(func=copy_registree_email_list)

    parser_email_registrees = subparsers.add_parser(
        "email_registrees", help="send an email to registrees"
    )
    parser_email_registrees.add_argument(
        "text_file", help="Text file to read the email subject and body from"
    )
    parser_email_registrees.set_defaults(func=send_email_to_registrees)

    args = parser.parse_args()
    args_dict = {}
    for k in vars(args):
        if k == 'unpaid_only':
            if getattr(args, k):
                args_dict['filter_attributes'] = [('paid_in_full', False)]
        elif k not in ('func',):
            args_dict[k] = getattr(args, k)
        
    if hasattr(args, 'func'):
        args.func(**args_dict)
