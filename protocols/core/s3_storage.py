import boto3
import json
import os
from django.conf import settings

class S3Storage:
    def __init__(self):
        self.bucket_name = os.environ.get('S3_BUCKET_NAME', 'protoscript-protocols')
        self.s3 = boto3.client(
            's3',
            endpoint_url=os.environ.get('S3_ENDPOINT_URL'),
            aws_access_key_id=os.environ.get('S3_ACCESS_KEY'),
            aws_secret_access_key=os.environ.get('S3_SECRET_KEY'),
            region_name=os.environ.get('S3_REGION', 'us-east-1')
        )

    def upload_json(self, key, data):
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=json.dumps(data),
            ContentType='application/json'
        )

    def upload_file(self, key, file_obj):
        self.s3.upload_fileobj(file_obj, self.bucket_name, key)

    def download_json(self, key):
        response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
        return json.loads(response['Body'].read().decode('utf-8'))

    def download_file(self, key, local_path):
        self.s3.download_file(self.bucket_name, key, local_path)

    def get_status(self, job_id):
        key = f"jobs/{job_id}/status.json"
        try:
            return self.download_json(key)
        except self.s3.exceptions.NoSuchKey:
            return None

    def update_status(self, job_id, status_data):
        key = f"jobs/{job_id}/status.json"
        # Merge with existing status if exists
        existing = self.get_status(job_id) or {}
        existing.update(status_data)
        self.upload_json(key, existing)

    def save_result(self, job_id, markdown_content):
        key = f"jobs/{job_id}/result.md"
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=markdown_content,
            ContentType='text/markdown'
        )

    def get_result(self, job_id):
        key = f"jobs/{job_id}/result.md"
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            return response['Body'].read().decode('utf-8')
        except self.s3.exceptions.NoSuchKey:
            return None

    def list_job_ids(self):
        # This lists prefixes under jobs/
        paginator = self.s3.get_paginator('list_objects_v2')
        job_ids = set()
        for page in paginator.paginate(Bucket=self.bucket_name, Prefix='jobs/', Delimiter='/'):
            for prefix in page.get('CommonPrefixes', []):
                # prefix['Prefix'] is something like 'jobs/uuid/'
                job_id = prefix['Prefix'].split('/')[1]
                if job_id:
                    job_ids.add(job_id)
        return list(job_ids)

    def delete_job(self, job_id):
        # Delete all objects with the job prefix
        paginator = self.s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=f'jobs/{job_id}/'):
            if 'Contents' in page:
                delete_keys = [{'Key': obj['Key']} for obj in page['Contents']]
                self.s3.delete_objects(Bucket=self.bucket_name, Delete={'Objects': delete_keys})
