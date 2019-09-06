import os, os.path

import docker

MARKDOWN_CONTAINER = ('markdown', 'registry.gitlab.com/md410_2020_conv/md410_2020_conv_reg_form_markdown_creator:latest')
PDF_CONTAINER = ('pdf', 'registry.gitlab.com/md410_2020_conv/md410_2020_conv_reg_form_pdf_creator:latest')

client = docker.from_env()

volumes = {os.getcwd(): {'bind':'/io', 'mode':'rw'}}

res = client.containers.run(MARKDOWN_CONTAINER[1], name=MARKDOWN_CONTAINER[0],
                            volumes=volumes, auto_remove=True, stdout=True, stderr=True, tty=False).decode('utf-8')
in_file = res.strip().split('/')[-1]
res = client.containers.run(PDF_CONTAINER[1], name=PDF_CONTAINER[0], command=f'/io/{in_file}',
                            volumes=volumes, auto_remove=True, stdout=True, stderr=True, tty=False).decode('utf-8')
print(str(res.strip()))

# if __name__ == '__main__':
#     import argparse
#     parser = argparse.ArgumentParser(description='Run a containerised kppe instance')
#     parser.add_argument('template', help='Template to use')
#     parser.add_argument('in_path', help='Path to the file to process')
#     parser.add_argument('--templates_dir', default=None, help='Template directory to use')
#     args = parser.parse_args()

#     if args.templates_dir and not os.path.exists(args.templates_dir):
#         print(f'Supplied templates dir "{args.templates_dir}" is not a valid path')
#         sys.exit(1)

#     call_kppe(args.template, args.in_path, templates_dir=args.templates_dir)
