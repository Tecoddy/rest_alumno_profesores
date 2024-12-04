import random
import string
import time
import boto3
from botocore.exceptions import NoCredentialsError
import uuid


# Configure AWS credentials
session = boto3.session.Session(
    aws_access_key_id="ASIASJGR52XF7MLSNOKX",
    aws_secret_access_key="TkgLFYhr0uU+V89nPYO0gkgOldR/wnLjg9KMO9bT",
    aws_session_token="IQoJb3JpZ2luX2VjEDgaCXVzLXdlc3QtMiJGMEQCIHxfObl8oS/063Q4NLeqdJxkcrEJahe5rRC4loqOrYmTAiAveMDZNtpoBhI1rDZY6oKXHdnrq6yNc74yqSqljCMKniqwAgjh//////////8BEAEaDDE1NzIwNjU2NjM0NyIM9JyT2Y1tIDNEvYq8KoQC4ngy6bdCdm+XrvB/nBZ52gncbn6suGeIlOMVxAbuk7VKjQVJauICfnpm/pNI8YA3OtRBwSR/5qIKCpK4sWjQm+nweRPRsm10dTw6plwSU8JPeWNjfjquue7TFWeoJHRpqUTnzjcOhhyUMZB1nSa9drDNY7ts5zizy/q5jyJNQU8UjRoW1dpTBcYwd+426YnKvgpTdSB5JwuQmBxSZF+a1eN+xodI6YAsEIM9uvO5y2yzIXbBxWpAPifkA2+t5HRzGNq78cfEAdfJCN2AGP+ZkGCj4ii+1lyo+DJFv1Toot5B+JJjVoKK0o9xcp1JNoTmQSOfDStv6baOPuaa3L9aovIEMTkw6L6+ugY6ngGYlkqHVjwR80xhy0M9RReq8zgFnFdcmURKzFcRlo8D+BN7imIwE4xcKS+6DvcGWR4lLhhRWvRf9+d4X+Y+CdWyw1+3+/JoEG/X9cUBQgzqKC1gt6DT4dVVV060NZPaH9rwSo960qN7UWDD/cmS2QIlIqcXu+1qsVsuQAFNr3jg09DvnM1vT0FbPq05hY//Ga5GaCDtaPCdYOjJNa2H0w==",
    region_name='us-east-1'  # Replace with your region
    )
s3 = session.client('s3')

# DynamoDB Client
dynamodb = boto3.resource('dynamodb', 
    aws_access_key_id="ASIASJGR52XF7MLSNOKX",
    aws_secret_access_key="TkgLFYhr0uU+V89nPYO0gkgOldR/wnLjg9KMO9bT",
    aws_session_token="IQoJb3JpZ2luX2VjEDgaCXVzLXdlc3QtMiJGMEQCIHxfObl8oS/063Q4NLeqdJxkcrEJahe5rRC4loqOrYmTAiAveMDZNtpoBhI1rDZY6oKXHdnrq6yNc74yqSqljCMKniqwAgjh//////////8BEAEaDDE1NzIwNjU2NjM0NyIM9JyT2Y1tIDNEvYq8KoQC4ngy6bdCdm+XrvB/nBZ52gncbn6suGeIlOMVxAbuk7VKjQVJauICfnpm/pNI8YA3OtRBwSR/5qIKCpK4sWjQm+nweRPRsm10dTw6plwSU8JPeWNjfjquue7TFWeoJHRpqUTnzjcOhhyUMZB1nSa9drDNY7ts5zizy/q5jyJNQU8UjRoW1dpTBcYwd+426YnKvgpTdSB5JwuQmBxSZF+a1eN+xodI6YAsEIM9uvO5y2yzIXbBxWpAPifkA2+t5HRzGNq78cfEAdfJCN2AGP+ZkGCj4ii+1lyo+DJFv1Toot5B+JJjVoKK0o9xcp1JNoTmQSOfDStv6baOPuaa3L9aovIEMTkw6L6+ugY6ngGYlkqHVjwR80xhy0M9RReq8zgFnFdcmURKzFcRlo8D+BN7imIwE4xcKS+6DvcGWR4lLhhRWvRf9+d4X+Y+CdWyw1+3+/JoEG/X9cUBQgzqKC1gt6DT4dVVV060NZPaH9rwSo960qN7UWDD/cmS2QIlIqcXu+1qsVsuQAFNr3jg09DvnM1vT0FbPq05hY//Ga5GaCDtaPCdYOjJNa2H0w==",
    region_name='us-east-1')  # Change region if needed
sessions_table = dynamodb.Table('sesiones-alumnos')

bucket_name = 'alumnos-fotos'

def upload_file(file,file_name,content_type) : 
    # Upload the file to S3
    s3.upload_fileobj(
        file,
        bucket_name,  # Replace with your bucket name
        file_name,
        ExtraArgs={'ContentType': content_type, 'ACL': 'public-read'}
    )
    return f"https://{bucket_name}.s3.amazonaws.com/{file_name}"

def enviar_notificacion_sns(mensaje):
    try:
        sns = session.client('sns')
        response = sns.publish(
            TopicArn="arn:aws:sns:us-east-1:157206566347:email",
            Message=mensaje
        )
        return response
    except Exception as e:
        raise RuntimeError(f"Error al enviar notificación: {str(e)}")
    
def login(id):
    # Generate sessionString and timestamp
    session_id = str(uuid.uuid4())
    session_string = ''.join(random.choices(string.ascii_letters + string.digits, k=128))
    timestamp = int(time.time())

    # Write the session to DynamoDB
    sessions_table.put_item(Item={
        'id': session_id,
        'fecha': timestamp,
        'alumnoId': id,
        'active': True,
        'sessionString': session_string
    })

    return {"id": session_id, "sessionString": session_string}

def verify_session(id, session_string):
    # Query DynamoDB for the session
    return sessions_table.scan(
        FilterExpression="alumnoId = :alumnoId AND sessionString = :sessionString",
        ExpressionAttributeValues={
            ":alumnoId": id,
            ":sessionString": session_string
        }
    )

def logout(id):
    sessions_table.update_item(
        Key={'id': id},
        UpdateExpression="SET active = :active",
        ExpressionAttributeValues={':active': False}
    )