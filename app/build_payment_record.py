""" Build an MDC2021 payment record from supplied reg num

"""
__author__ = "K van Wyk"
__version__ = "0.0.1"
from datetime import date
import os, os.path


from md410_2021_conv_common import db

import create_payment_record_markdown
from upload_data import parse_data_file

import docker
import pyperclip
import s3

PDF_CONTAINER = (
    "pdf",
    "registry.gitlab.com/md410_2021_conv/md410_2021_conv_pdf_creator:latest",
)


def build_doc(registree_set, pull=False):
    client = docker.from_env()

    volumes = {os.getcwd(): {"bind": "/io", "mode": "rw"}}
    if pull:
        for c in [cont for (k, cont) in globals().items() if "CONTAINER" in k]:
            print(f"Pulling {c[1]}")
            client.images.pull(c[1])

    fn = create_payment_record_markdown.main(
        registree_set=registree_set, out_dir="."
    ).split("/")[-1]
    res = client.containers.run(
        PDF_CONTAINER[1],
        name=PDF_CONTAINER[0],
        command=f"/io/{fn}",
        volumes=volumes,
        auto_remove=True,
        stdout=True,
        stderr=True,
        tty=False,
    ).decode("utf-8")
    return f"{os.path.splitext(fn)[0]}.pdf"


def process_reg_data(reg_num, pull=False):
    s = s3.S3(reg_num)
    dbh = db.DB()
    registree_set = dbh.get_registrees(reg_num)
    fn = build_doc(registree_set, pull)
    s.upload_pdf_file(fn)
    print(f"Processed payment details for reg num {registree_set.reg_num}. File: {fn}")
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
        "--pull", action="store_true", help="Whether to also pull fresh containers"
    )
    args = parser.parse_args()
    process_reg_data(args.reg_num, pull=args.pull)
