import aws_credentials

import boto3


class S3(object):
    def __init__(self, reg_num):
        self.session = boto3.Session(
            aws_access_key_id=aws_credentials.ACCESS_KEY,
            aws_secret_access_key=aws_credentials.SECRET_KEY,
        )
        self.resource = self.session.resource("s3")
        self.reg_num = reg_num

    def download_data_file(self):
        d = self.resource.Object(
            bucket_name="md410-2020-conv", key=f"reg_forms/{self.reg_num:03}/data.json"
        )
        d.download_file("data.json")


if __name__ == "__main__":
    s3 = S3(18)
    s3.download_data_file()
