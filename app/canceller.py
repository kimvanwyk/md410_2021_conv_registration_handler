""" Registration canceller
"""

from md410_2021_conv_common.db import DB

import pyperclip

import os, os.path


class Error(Exception):
    pass


def process(orig_reg_nums):
    out = []
    dbh = DB()
    reg_nums = []
    for rn in orig_reg_nums:
        rns = [r.reg_num for r in dbh.get_registrees(rn)]
        if rns:
            reg_nums.extend(rns)
            registrees = dbh.get_all_registrees(rns)
            names = " and ".join(
                [f"{r.titled_first_names} {r.last_name}" for r in registrees]
            )
            reg_num_string = "/".join([f"{r.reg_num:03}" for r in registrees])
            total = sum(r.payments for r in registrees)
            out.append(f"{names}, MDC{reg_num_string}, R{total}:")

    dbh.cancel_registration(reg_nums)
    return out


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "reg_nums",
        nargs="+",
        type=int,
        help="The reg numbers to cancel. Use only 1 per pair",
    )
    args = parser.parse_args()

    titles = process(args.reg_nums)
    print("\n\n".join(titles))
    pyperclip.copy("\n\n".join(titles))
