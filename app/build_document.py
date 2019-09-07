import os, os.path

import docker

import s3

MARKDOWN_CONTAINER = ('markdown', 'registry.gitlab.com/md410_2020_conv/md410_2020_conv_reg_form_markdown_creator:latest')
PDF_CONTAINER = ('pdf', 'registry.gitlab.com/md410_2020_conv/md410_2020_conv_reg_form_pdf_creator:latest')

def build_doc():
    client = docker.from_env()

    volumes = {os.getcwd(): {'bind':'/io', 'mode':'rw'}}

    res = client.containers.run(MARKDOWN_CONTAINER[1], name=MARKDOWN_CONTAINER[0],
                                volumes=volumes, auto_remove=True, stdout=True, stderr=True, tty=False).decode('utf-8')
    in_file = res.strip().split('/')[-1]
    res = client.containers.run(PDF_CONTAINER[1], name=PDF_CONTAINER[0], command=f'/io/{in_file}',
                                volumes=volumes, auto_remove=True, stdout=True, stderr=True, tty=False).decode('utf-8')
    return f"{os.path.splitext(in_file)[0]}.pdf"

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Create a registration form report from a given registration number ')
    parser.add_argument('reg_num', type=int)
    args = parser.parse_args()

    s = s3.S3(args.reg_num)
    s.download_data_file()
    fn = build_doc()
    s.upload_pdf_file(fn)
