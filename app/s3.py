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
        fn = 'data.json'
        d = self.resource.Object(
            bucket_name="md410-2020-conv", key=f"reg_forms/{self.reg_num:03}/data.json"
        )
        d.download_file(fn)
        return fn

    def upload_pdf_file(self, fn):
        d = self.resource.Object(
            bucket_name="md410-2020-conv", key=f"reg_forms/{self.reg_num:03}/{fn}"
        )
        d.upload_file(fn)

    def download_pdf_file(self, reg_num, pattern):
        bucket = self.resource.Bucket("md410-2020-conv")
        objects = bucket.objects.all()
        for obj in objects:
            if all(item in obj.key for item in (f"{reg_num:03}", pattern, ".pdf")):
                fn = obj.key.rsplit('/')[-1]
                d = self.resource.Object(bucket_name=obj.bucket_name, key=obj.key)
                d.download_file(fn)
                break
        return fn

    def download_pdf_reg_file(self, reg_num):
        return self.download_pdf_file(reg_num, "mdc2020_registration")
        
    def download_pdf_payment_file(self, reg_num):
        return self.download_pdf_file(reg_num, "mdc2020_payments")
        
if __name__ == "__main__":
    s3 = S3(18)
    s3.upload_pdf_file("mdc2020_registration_018_k_van_wyk_v_van_wyk.pdf")
