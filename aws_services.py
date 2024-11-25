import random
import string
import time
import boto3
from botocore.exceptions import NoCredentialsError
import uuid


# Configure AWS credentials
session = boto3.session.Session(
    aws_access_key_id="ASIASJGR52XFXR54XEVR",
    aws_secret_access_key="OEjcALbddyJvw8M2ERQWdS5oQGxvxAeE4zqjzufH",
    aws_session_token="IQoJb3JpZ2luX2VjEHAaCXVzLXdlc3QtMiJHMEUCIQDaUJHhNwmYV7X0M5k8MS5XvCZ5IMdZYtZX2x1Ffr9KgQIgcV7z0woGe+iAj6OP3rciCCvq+OEsJM7IMThfnwpt7VoqpwIIGRABGgwxNTcyMDY1NjYzNDciDDNlnRS2JDYoQGGtiiqEAk+E8543Ra4SUsfwiGZiAMM/Ma6BPdG//NQGoi2vaidNsGzH8PNkhBnf76HnkTj62Uva/+kIiUnGw3e+sIpOTIVxgiA8sunschCf5CPfU9Xcx/Uyc9ZFWTmRa4sQVYjDFHdGfCUHHi1bseGzf7aGpSJeGih94sy3jX/abJrCm9hDMtBwRpY1AKLsqr5OtuCf5vbcJc+sBnt/rAPT8gI+wqREgvMmU7576EldqmWgZcoApaM5m3lh+HFgXXeZnPaIbBAdvvGKnx9DvljHmx1sGAZn/S1Yq/wVfgZjynYfGt9G6fLMI41yy0B1ASPONK7GTJdJRV5ahK/ykcVe2egDzsRXwr+KMOW3kroGOp0BAaVgkjXa8zt7yRepCVu3xL9BcadFQKmH17PZwCdfxKDpqdsWVI/lUsBjRIZ6Do4ObpzxM6eDddnFoQDP1/X29T+h9GZ6uVVbjtQi2A3XlvldsNd7hvz/JUbDLxWJrSGZR/E3HHGTjEB9OT/h0V/OWvueAAcIVHEboWqpknCdUFlY1AfcYdUtDcKU0zLHCEqxTcjA4pnDH5Fda36Dbg==",
    region_name='us-east-1'  # Replace with your region
    )
s3 = session.client('s3')

# DynamoDB Client
dynamodb = boto3.resource('dynamodb', 
    aws_access_key_id="ASIASJGR52XFXR54XEVR",
    aws_secret_access_key="OEjcALbddyJvw8M2ERQWdS5oQGxvxAeE4zqjzufH",
    aws_session_token="IQoJb3JpZ2luX2VjEHAaCXVzLXdlc3QtMiJHMEUCIQDaUJHhNwmYV7X0M5k8MS5XvCZ5IMdZYtZX2x1Ffr9KgQIgcV7z0woGe+iAj6OP3rciCCvq+OEsJM7IMThfnwpt7VoqpwIIGRABGgwxNTcyMDY1NjYzNDciDDNlnRS2JDYoQGGtiiqEAk+E8543Ra4SUsfwiGZiAMM/Ma6BPdG//NQGoi2vaidNsGzH8PNkhBnf76HnkTj62Uva/+kIiUnGw3e+sIpOTIVxgiA8sunschCf5CPfU9Xcx/Uyc9ZFWTmRa4sQVYjDFHdGfCUHHi1bseGzf7aGpSJeGih94sy3jX/abJrCm9hDMtBwRpY1AKLsqr5OtuCf5vbcJc+sBnt/rAPT8gI+wqREgvMmU7576EldqmWgZcoApaM5m3lh+HFgXXeZnPaIbBAdvvGKnx9DvljHmx1sGAZn/S1Yq/wVfgZjynYfGt9G6fLMI41yy0B1ASPONK7GTJdJRV5ahK/ykcVe2egDzsRXwr+KMOW3kroGOp0BAaVgkjXa8zt7yRepCVu3xL9BcadFQKmH17PZwCdfxKDpqdsWVI/lUsBjRIZ6Do4ObpzxM6eDddnFoQDP1/X29T+h9GZ6uVVbjtQi2A3XlvldsNd7hvz/JUbDLxWJrSGZR/E3HHGTjEB9OT/h0V/OWvueAAcIVHEboWqpknCdUFlY1AfcYdUtDcKU0zLHCEqxTcjA4pnDH5Fda36Dbg==",
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