""" Obtain a reg form record for a given reg number and provide email steps
"""

import os.path

from md410_2020_conv_common.db import DB
import s3

import attr
import pyperclip

BCC = "; ".join(["print.image@intekom.co.za", "david.shone.za@gmail.com"])
with open("reg_form_msg.txt", "r") as fh:
    BODY = fh.read()


def send_email(reg_num=None, registree_set=None, fn=None):
    if fn is None:
        s = s3.S3(reg_num)
        fn = s.download_pdf_reg_file(reg_num)

    if reg_num is not None:
        db = DB()
        registree_set = db.get_registrees(args.reg_num)
    elif registree_set is None:
        raise ValueError(
            "Either a reg num to look up or a RegistreeSet should be provided"
        )

    reg_num = f"MDC{registree_set.reg_num:003}"
    emails = "; ".join(set([r.email for r in registree_set.registrees if r.email]))
    deposit = 300 * len(registrees)

    if emails:
        pyperclip.copy(emails)
        print(f"To: addresses copied to clipboard: {emails}")
        input()
        pyperclip.copy(BCC)
        print(f"BCC: addresses copied to clipboard: {BCC}")
        input()
        subject = f'Registration for 2020 MD410 Convention for {full_names}. Registration number{"s" if len(registrees) > 1 else ""}: {reg_nums}'
        pyperclip.copy(subject)
        print(f"Subject copied to clipboard: {subject}")
        input()
        body = BODY.format(**locals())
        pyperclip.copy(body)
        print(body)
        input()
        pyperclip.copy(fn)
        print(os.path.abspath(fn))
    else:
        print("No email addresses supplied")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("reg_num", type=int, help="Registration number")
    args = parser.parse_args()
    send_email(args.reg_num)
