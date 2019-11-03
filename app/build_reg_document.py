""" Build an MDC2020 registration record from supplied reg num

"""
__author__ = "K van Wyk"
__version__ = "0.0.1"
import os, os.path

import docker

import pika
import s3

UPLOAD_CONTAINER = ('upload', 'registry.gitlab.com/md410_2020_conv/md410_2020_conv_reg_form_data_uploader:latest')
MARKDOWN_CONTAINER = ('markdown', 'registry.gitlab.com/md410_2020_conv/md410_2020_conv_reg_form_markdown_creator:latest')
PDF_CONTAINER = ('pdf', 'registry.gitlab.com/md410_2020_conv/md410_2020_conv_reg_form_pdf_creator:latest')
NETWORK = "container:md4102020convregformserverconfig_postgres_1"
QUEUE_NAME = 'reg_form'

def build_doc(reg_num):
    client = docker.from_env()

    volumes = {os.getcwd(): {'bind':'/io', 'mode':'rw'}}
    for c in [cont for (k,cont) in globals().items() if 'CONTAINER' in k]:
        print(f'Pulling {c[1]}')
        client.images.pull(c[1])
        
    res = client.containers.run(UPLOAD_CONTAINER[1], name=UPLOAD_CONTAINER[0], command=f"/io/data.json",
                                network=NETWORK, volumes=volumes, auto_remove=True, stdout=True, stderr=True, tty=False).decode('utf-8')

    res = client.containers.run(MARKDOWN_CONTAINER[1], name=MARKDOWN_CONTAINER[0], command=f"{reg_num}",
                                network=NETWORK, volumes=volumes, auto_remove=True, stdout=True, stderr=True, tty=False).decode('utf-8')
    in_file = res.strip().split('/')[-1]

    res = client.containers.run(PDF_CONTAINER[1], name=PDF_CONTAINER[0], command=f'/io/{in_file}',
                                network=NETWORK, volumes=volumes, auto_remove=True, stdout=True, stderr=True, tty=False).decode('utf-8')
    return f"{os.path.splitext(in_file)[0]}.pdf"

def process_reg_data(reg_num):
    s = s3.S3(reg_num)
    s.download_data_file()
    fn = build_doc(reg_num)
    s.upload_pdf_file(fn)
    print(f"processed reg num {reg_num}")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "reg_num", type=int, help="Registration number"
    )
    args = parser.parse_args()
    process_reg_data(args.reg_num)