import boto3

class aws_session:
    def __init__(self, **kwargs):
        # Create AWS session
        aws_session = boto3.Session(
            aws_access_key_id=kwargs.get('access_key'),
            aws_secret_access_key=kwargs.get('secret_key'),
        )

        # Create low-level STS client
        sts_client = aws_session.client('sts')

        # Retrieve temporary session credentials for assumed role
        temp_creds = sts_client.assume_role(
            RoleArn=kwargs.get('role_arn'),
            RoleSessionName="sts-session"
        )

        self.temp_session = boto3.Session(
            aws_access_key_id=temp_creds['Credentials']['AccessKeyId'],
            aws_secret_access_key=temp_creds['Credentials']['SecretAccessKey'],
            aws_session_token=temp_creds['Credentials']['SessionToken'],
            region_name=kwargs.get('region')
        )

    def dynamodb_resource(self):
        dynamodb = self.temp_session.resource('dynamodb')
        return dynamodb
