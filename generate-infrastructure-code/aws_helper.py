import base64
import boto3
import json

from botocore.exceptions import ClientError
from common.custom_logging import CustomLogger


logger = CustomLogger().logger


### AWS 
def get_secret_value(secret_name):
    '''

    '''
    # Create a Secrets Manager client
    client = boto3.client('secretsmanager')

    try:
        response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e.response['Error']['Code']

        if e.response['Error']['Code'] == 'AccessDeniedException':
            exception_metadata['ErrorCode'] = 401
            exception_metadata['ErrorCode'] = "Access denied to access secret"
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            exception_metadata['ErrorCode'] = 500
            exception_metadata['ErrorCode'] = e.response['Error']['Message']
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            exception_metadata['ErrorCode'] = 400
            exception_metadata['ErrorCode'] = "Invalid parameter for AWS Secrets Manager"
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            exception_metadata['ErrorCode'] = 400
            exception_metadata['ErrorCode'] = "Invalid request to AWS Secrets Manager"
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            exception_metadata['ErrorCode'] = 400
            exception_metadata['ErrorCode'] = "Unable to find requested AWS secret"
        else:
            exception_metadata['ErrorCode'] = e.response['ResponseMetadata']['HTTPStatusCode']
            exception_metadata['Message'] = e.response['Error']['Message']

        raise Exception(exception_metadata)
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 500
        exception_metadata['Message'] = "Unable delete directory."

        raise Exception(exception_metadata)
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in response:
            secret = json.loads(response['SecretString'])

            for item in secret:
                secret = secret[item]
        else:
            secret = base64.b64decode(response['SecretBinary'])

        return secret


def assume_role(aws_account_number, role_name, session=None):
    '''
    
    '''
    # Determine if the request to assume role is coming from the execution role
    # or existing session
    try:
        if session is None:
            logger.debug("Request to assume role is from Lambda Exeuction Role")
            sts_client = boto3.client('sts')
        else:
            logger.debug("Request to assume role is from existing session")
            sts_client = session.client('sts')
    except botocore.exceptions.ClientError as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e.response['Error']['Code']

        if e.response['Error']['Code'] == "AccessDeniedException":
            exception_metadata['ErrorCode'] = 401
            exception_metadata['Message'] = "Access denied to create STS session"
        else: 
            exception_metadata['ErrorCode'] = e.response['ResponseMetadata']['HTTPStatusCode']
            exception_metadata['Message'] = e.response['Error']['Message']

        raise Exception(exception_metadata)
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 500
        exception_metadata['Message'] = "Unable to create Boto3 STS session" 

        raise Exception(exception_metadata)

    # Get the current partition
    partition = sts_client.get_caller_identity()['Arn'].split(":")[1]

    # Start assuming the role
    response = sts_client.assume_role(
        RoleArn='arn:{}:iam::{}:role/{}'.format(
            partition,
            aws_account_number,
            role_name
        ),
        RoleSessionName='GenerateInfrastructureCode'
    )

    # Storing STS credentials
    session = boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken']
    )
    logger.debug(f"Session created for account {aws_account_number}, role {role_name}")

    return session


def get_account_alias(account_id, session=None):
    '''
    '''
    try:
        if session is None:
            logger.debug("Request to assume role is from Lambda Exeuction Role")
            org_client = boto3.client('organizations')
        else:
            logger.debug("Request to assume role is from existing session")
            org_client = session.client('organizations')
    except botocore.exceptions.ClientError as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e.response['Error']['Code']

        if e.response['Error']['Code'] == "AccessDeniedException":
            exception_metadata['ErrorCode'] = 401
            exception_metadata['Message'] = "Access denied to create session for Organizations"
        else: 
            exception_metadata['ErrorCode'] = e.response['ResponseMetadata']['HTTPStatusCode']
            exception_metadata['Message'] = e.response['Error']['Message']
        raise Exception(exception_metadata)
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 500
        exception_metadata['Message'] = "Unable to create Boto3 client for Organizations" 

        raise Exception(exception_metadata)

    logger.info(f"Searching for account alias for {account_id}")
    try:
        response = org_client.describe_account(
            AccountId=account_id    
        )

        logger.debug(response)  
    except botocore.exceptions.ClientError as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e.response['Error']['Code']

        if e.response['Error']['Code'] == "AccessDeniedException":
            exception_metadata['ErrorCode'] = 401
            exception_metadata['ErrorCode'] = "Access denied to describe AWS account via Organizations API"
        elif e.response['Error']['Code'] == "ResourceNotFoundException":
            exception_metadata['ErrorCode'] = 400
            exception_metadata['ErrorCode'] = "Unable to find AWS account via Organizations API"
        else:
            exception_metadata['ErrorCode'] = e.response['ResponseMetadata']['HTTPStatusCode']
            exception_metadata['Message'] = e.response['Error']['Message']

        raise Exception(exception_metadata)
    except Exception as e:
        exception_metadata = dict()
        exception_metadata['Error'] = e
        exception_metadata['ErrorCode'] = 400
        exception_metadata['Message'] = "Unable to describe AWS account via Organizations API" 

        raise Exception(exception_metadata)

    if response['Account'].get('Name'):
        account_alias = response['Account']['Name']

        logger.debug(f"Account ({account_id}) alias is {account_alias}")
        
        return account_alias
    else:
        return None


