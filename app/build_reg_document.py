""" Build an MDC2021 registration record from supplied reg num

"""
__author__ = "K van Wyk"
__version__ = "0.0.1"
from datetime import date
import os, os.path


# from md410_2020_conv_common.db import DB
import sys

sys.path.insert(0, "/home/kimv/src/md410_2020_conv_common/md410_2020_conv_common")
import db

import create_registration_record_markdown
from upload_data import parse_data_file

import docker
import pyperclip
import s3

PDF_CONTAINER = (
    "pdf",
    "registry.gitlab.com/md410_2020_conv/md410_2020_conv_reg_form_pdf_creator:latest",
)
NETWORK = "container:md410_2020_conv_reg_form_server_config_postgres_1"


def build_doc(registree_set, pull=False):
    client = docker.from_env()

    volumes = {os.getcwd(): {"bind": "/io", "mode": "rw"}}
    if pull:
        for c in [cont for (k, cont) in globals().items() if "CONTAINER" in k]:
            print(f"Pulling {c[1]}")
            client.images.pull(c[1])

    fn = create_registration_record_markdown.main(
        registree_set=registree_set, out_dir="."
    )

    res = client.containers.run(
        PDF_CONTAINER[1],
        name=PDF_CONTAINER[0],
        command=f"/io/{fn}",
        network=NETWORK,
        volumes=volumes,
        auto_remove=True,
        stdout=True,
        stderr=True,
        tty=False,
    ).decode("utf-8")
    return f"{os.path.splitext(fn)[0]}.pdf"


def process_reg_data(reg_num, rebuild=False, pull=False):
    s = s3.S3(reg_num)
    dbh = db.DB()
    if not rebuild:
        fn = s.download_data_file()

        registree_set = parse_data_file(fn)
        payees = dbh.get_2020_payees()
        print(f"Registrees: {registree_set.registree_names}")
        print(
            "Should any of the below payments from 2020 be applied to this registration?"
        )
        for (r, (name, amt)) in payees.items():
            print(f"{r:003}: {name}: R{amt}")
        print()
        previously_paid = 0
        while True:
            payee_reg = input("Applicable reg num: ")
            if not payee_reg:
                break
            previously_paid += payees[int(payee_reg)][-1]
        if previously_paid:
            registree_set.payments = [
                db.Payment(date(year=2020, month=5, day=1), previously_paid)
            ]
            registree_set.process_payments()
        dbh.save_registree_set(registree_set)

    else:
        registree_set = dbh.get_registrees(reg_num)
    fn = build_doc(registree_set, pull)
    s.upload_pdf_file(fn)
    print(
        f"{'re' if rebuild else ''}processed reg num {registree_set.reg_num}. File: {fn}"
    )
    pyperclip.copy(f"evince {fn} &")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "reg_num",
        type=int,
        help="The registration number to download data from or reprocess",
    )
    parser.add_argument(
        "--rebuild", action="store_true", help="Rebuild the supplied reg_num only",
    )
    parser.add_argument(
        "--pull", action="store_true", help="Whether to also pull fresh containers"
    )
    args = parser.parse_args()
    process_reg_data(args.reg_num, rebuild=args.rebuild, pull=args.pull)
