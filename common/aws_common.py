import boto3
from botocore.exceptions import ClientError

ERROR_HELP_STRINGS = {
    # Operation specific errors
    'ResourceInUseException': 'Request rejected because it tried to delete a table currently in the CREATING state, retry again after a while',
    'LimitExceededException': 'Request rejected because it has exceeded the allowed simultaneous table operations i.e, 50.' +
                              'These operations include CreateTable, UpdateTable, DeleteTable,UpdateTimeToLive, RestoreTableFromBackup, and RestoreTableToPointInTime',
    # Common Errors
    'InternalServerError': 'Internal Server Error, generally safe to retry with exponential back-off',
    'ProvisionedThroughputExceededException': 'Request rate is too high. If you\'re using a custom retry strategy make sure to retry with exponential back-off.' +
                                              'Otherwise consider reducing frequency of requests or increasing provisioned capacity for your table or secondary index',
    'ResourceNotFoundException': 'One of the tables was not found, verify table exists before retrying',
    'ServiceUnavailable': 'Had trouble reaching DynamoDB. generally safe to retry with exponential back-off',
    'ThrottlingException': 'Request denied due to throttling, generally safe to retry with exponential back-off',
    'UnrecognizedClientException': 'The request signature is incorrect most likely due to an invalid AWS access key ID or secret key, fix before retrying',
    'ValidationException': 'The input fails to satisfy the constraints specified by DynamoDB, fix input before retrying',
    'RequestLimitExceeded': 'Throughput exceeds the current throughput limit for your account, increase account level throughput before retrying',
}

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

    def delete_dynamodb_table(self, dynamodb_table):
        try:
            response = dynamodb_table.delete()
            print("Successfully deleted table.")
            # Handle response
        except ClientError as error:
            self._handle_error(error)
        except BaseException as error:
            #print("Unknown error while deleting table: " + error.response['Error']['Message'])
            print(error)


    def create_dynamodb_table(self, dynamodb_resource, input):
        try:
            response = dynamodb_resource.create_table(**input)
            print("Successfully created table.")
            return response
        except ClientError as error:
            self._handle_error(error)
        except BaseException as error:
            #print("Unknown error while deleting table: " + error.response['Error']['Message'])
            print(error)
    def _handle_error(self, error):
        error_code = error.response['Error']['Code']
        error_message = error.response['Error']['Message']

        error_help_string = ERROR_HELP_STRINGS[error_code]

        print('[{error_code}] {help_string}. Error message: {error_message}'
              .format(error_code=error_code,
                      help_string=error_help_string,
                      error_message=error_message))

