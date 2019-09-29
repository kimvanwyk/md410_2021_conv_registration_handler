import os, os.path

import docker

import pika
import s3

UPLOAD_CONTAINER = ('upload', 'registry.gitlab.com/md410_2020_conv/md410_2020_conv_reg_form_data_uploader:latest')
MARKDOWN_CONTAINER = ('markdown', 'registry.gitlab.com/md410_2020_conv/md410_2020_conv_reg_form_markdown_creator:latest')
PDF_CONTAINER = ('pdf', 'registry.gitlab.com/md410_2020_conv/md410_2020_conv_reg_form_pdf_creator:latest')
NETWORK = "container:md410_2020_conv_postgres"
QUEUE_NAME = 'reg_form'

def build_doc(reg_num):
    client = docker.from_env()

    volumes = {os.getcwd(): {'bind':'/io', 'mode':'rw'}}

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

def queue_callback(ch, method, properties, body):
    process_reg_data(int(body))

def handle_queue():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_consume(
        queue=QUEUE_NAME, on_message_callback=queue_callback, auto_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    handle_queue()
