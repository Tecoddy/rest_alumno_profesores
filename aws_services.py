import random
import string
import time
import boto3
from botocore.exceptions import NoCredentialsError
import uuid


# Configure AWS credentials
session = boto3.session.Session(
    aws_access_key_id="ASIASJGR52XF4FL44BYT",
    aws_secret_access_key="/cnTNFOSL+uO0Q3jMW59b+bLOYpsX8hIXqwteABj",
    aws_session_token="IQoJb3JpZ2luX2VjEGIaCXVzLXdlc3QtMiJGMEQCIAVeDN3uu0vKqWOa0TTrp2k1Gnq2vHH0J8DsAJDysKpfAiBZzQp+MLMSZVGKACyfWxTYkKoJhb3wrNJgQRoanhYclSqwAgj7//////////8BEAEaDDE1NzIwNjU2NjM0NyIMYEdaksVFcbkRIO2UKoQCyvielLy+ZrPnvEREpSRzq2sZfr0foExLTNB+sQZZ2yp3hbu+m8UNgdRIIdYSeX5KUOcy6jqJ7OOW1XGGtK8zMp402obo5ZoWXUzciR+hI1EjtQVbw0u7iMpYnViooMMjCc6kXx//qhFHWwXcOCEXUVzKCQP4mxZHHJ22BnmguaFFv+tHUpXXSE0DdyKzHfKCWaczkq7Z9pTwHJxF+01PwDqocc2A00JO0zvtagUvJi4aGz+gbbu7amBaM1QwZ0y+YJy37YVWI5WbV6d81vL5eFylZMy85ayVRqhHCpLrgpeaPYU89ZDc4nAJzy/Azsov3IQazrXn6GEN839kxmeG6+K5qhEwsaSPugY6ngGsWPk1X8E9seoi1K2nrB8R2vp1Kugo0ZyaJCl+5VsRI/j1m+wvqjBHxFzjbtId4ehFab2L/k7ID6JdZ//Bo13xmWJPfES2lUzQFRIG4MUoh1NIdIzPs68Y3o98GMhi8iKoTddd+kvTSPfdbYpIxxjaYle1v7YTJ9BjR3xLqTRYrDQbI2qTpZUzR1oUUZ6asUpG6tsITNul9PhAntXiPw==",
    region_name='us-east-1'  # Replace with your region
    )
s3 = session.client('s3')

# DynamoDB Client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Change region if needed
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