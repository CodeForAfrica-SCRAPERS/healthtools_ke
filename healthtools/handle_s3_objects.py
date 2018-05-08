import argparse
import logging
import boto3
import botocore

from botocore.exceptions import ClientError

from healthtools.config import AWS

log = logging.getLogger(__name__)

class S3ObjectHandler(object):
    """
    Check or create S3 objects (keys) as per the expected solutions
    """

    def __init__(self, s3):
        self.s3_object = s3

    def handle_s3_objects(self, bucket_name, key):
        """
        Scraper checks that the AWS S3 bucket exist. If it does, it has the
        expected structure contrary to which the scraper will
        create the structure as expected.
        """

        _s3 = boto3.resource("s3", **{
            "aws_access_key_id": AWS["aws_access_key_id"],
            "aws_secret_access_key": AWS["aws_secret_access_key"],
            "region_name": AWS["region_name"]
        })

        exists = True
        try:
            _s3.meta.client.head_bucket(Bucket=bucket_name)
        except botocore.exceptions.ClientError as err:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = int(err.response['Error']['Code'])
            if error_code == 404:
                exists = False

        if exists:
            create_bucket_msg = ("Error (BucketAlreadyExists): "
                                 "The requested bucket name %s already exists. "
                                 "Select a different name and try again." % bucket_name)
        else:
            # Create S3 Bucket if not exist
            response = self.s3_object.create_bucket(
                ACL='private',
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': AWS["region_name"]},
            )
            exists = True
            create_bucket_msg = response["ResponseMetadata"]["HTTPStatusCode"]

        # Create keys and files
        create_key_msg = self.create_keys(exists, bucket_name, key)

        create_key_msg["create_bucket_msg"] = create_bucket_msg
        return create_key_msg

    def create_keys(self, exists, bucket_name, key):
        """
        Scraper checks or creates the bucket structure as expected.
        """

        if exists:
            try:
                # Amazon S3 will overwrite a key if it exists.
                # And we definitely do not want that to happen

                # Returns some or all (up to 1000) of the objects in a bucket
                response = self.s3_object.list_objects(Bucket=bucket_name)

                s3_keys = []
                if "Contents" in response:
                    s3_keys = [contents['Key']
                               for contents in response["Contents"]]

                # Check if the key exists. If not create it.
                if not s3_keys or key not in s3_keys:
                    new_key = self.s3_object.put_object(ACL='private',
                                                        Bucket=bucket_name,
                                                        Key=key,
                                                        )

                    s3_keys += [key]
                    create_key_msg = "New key created successfully"

                else:
                    create_key_msg = ("Key already exists. "
                                      "Select a different name and try again.")

                msg = {"create_key_msg": create_key_msg}
                return msg

            except botocore.exceptions.ClientError as err:
                log.error(err)
