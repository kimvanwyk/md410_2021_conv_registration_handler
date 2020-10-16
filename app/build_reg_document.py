""" Build an MDC2021 registration record from supplied reg num

"""
__author__ = "K van Wyk"
__version__ = "0.0.1"
from datetime import date
import os, os.path



# from md410_2020_conv_common.db import DB
import sys
sys.path.insert(0, "/home/kimv/src/md410_2020_conv_common/md410_2020_conv_common")
from db import DB

import sys
sys.path.insert(0, "/home/kimv/src/md410_2020_conv_reg_form_markdown_creator/app/")
import create_registration_record_markdown

from upload_data import upload_reg_form

import docker
import pyperclip
import s3

MARKDOWN_CONTAINER = (
    "markdown",
    "registry.gitlab.com/md410_2020_conv/md410_2020_conv_reg_form_markdown_creator:latest",
)
PDF_CONTAINER = (
    "pdf",
    "registry.gitlab.com/md410_2020_conv/md410_2020_conv_reg_form_pdf_creator:latest",
)
NETWORK = "container:md410_2020_conv_reg_form_server_config_postgres_1"
QUEUE_NAME = "reg_form"


def build_doc(reg_num, pull=False):
    client = docker.from_env()

    volumes = {os.getcwd(): {"bind": "/io", "mode": "rw"}}
    if pull:
        for c in [cont for (k, cont) in globals().items() if "CONTAINER" in k]:
            print(f"Pulling {c[1]}")
            client.images.pull(c[1])

    # res = client.containers.run(
    #     MARKDOWN_CONTAINER[1],
    #     name=MARKDOWN_CONTAINER[0],
    #     command=f"{reg_num}",
    #     network=NETWORK,
    #     volumes=volumes,
    #     environment={'PGPASSWORD': os.getenv('PGPASSWORD')},
    #     auto_remove=True,
    #     stdout=True,
    #     stderr=True,
    #     tty=False,
    # ).decode("utf-8")
    # in_file = res.strip().split("/")[-1]
    create_registration_record_markdown.main(reg_num, ".", True)

    res = client.containers.run(
        PDF_CONTAINER[1],
        name=PDF_CONTAINER[0],
        command=f"/io/{in_file}",
        network=NETWORK,
        volumes=volumes,
        auto_remove=True,
        stdout=True,
        stderr=True,
        tty=False,
    ).decode("utf-8")
    return f"{os.path.splitext(in_file)[0]}.pdf"


def process_reg_data(reg_num, rebuild=False, pull=False):
    # s = s3.S3(reg_num)
    if not rebuild:
        # fn = s.download_data_file()
        fn = "data.json"
        (first_attendee, second_attendee) = upload_reg_form(fn)
        db = DB()
        payees = db.get_2020_payees()
        registrees = [f"{first_attendee.first_names} {first_attendee.last_name}"]
        if second_attendee:
            registrees.append(f"{second_attendee.first_names} {second_attendee.last_name}")
        print(f"Registrees: {'; '.join(registrees)}")
        print("Should any of the below payments from 2020 be applied to this registration?")
        for (r, (name, amt)) in payees.items():
            print(f"{r:003}: {name}: R{amt}")
        print()
        previous_payments = 0
        while True:
            payee_reg = input("Applicable reg num: ")
            if not payee_reg:
                break
            previous_payments += payees[int(payee_reg)][-1]
        print(previous_payments)
        db.set_reg_nums(first_attendee.reg_num)
        db.record_payment(previous_payments, date(year=2020, month=5, day=1))

    fn = build_doc(reg_num, pull)
    s.upload_pdf_file(fn)
    print(f"processed reg num {reg_num}. File: {fn}")
    pyperclip.copy(f"evince {fn} &")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("reg_num", type=int, help="Registration number")
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Rebuild only, no S3 download or DB upload",
    )
    parser.add_argument("--pull", action="store_true", help="Whether to also pull fresh containers")
    args = parser.parse_args()
    process_reg_data(args.reg_num, args.rebuild, args.pull)
