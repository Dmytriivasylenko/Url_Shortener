import time

import boto3
import json
import os

def resolve_url(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    short_code = event['pathParameters']['shortCode']

    if not short_code:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Short code is required'})
        }

    try:
        response = table.get_item(Key={'short_key': short_code})

        if 'Item' in response:
            item = response['Item']

            # Перевіряємо, чи не закінчився час дії
            expire_at = item.get('expire_at')
            if expire_at and int(time.time()) > expire_at:
                return {
                    'statusCode': 410,
                    'body': json.dumps({'message': 'This short URL has expired.'})
                }

            if item.get('used', False):
                return {
                    'statusCode': 410,
                    'body': json.dumps({'message': 'This short URL has already been used.'})
                }

            long_url = item.get('long_url')
            if long_url:
                table.update_item(
                    Key={'short_key': short_code},
                    UpdateExpression="set used = :val",
                    ExpressionAttributeValues={':val': True}
                )
                return {
                    'statusCode': 302,
                    'headers': {'Location': long_url}
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'message': 'Short URL found, but long URL is missing'})
                }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Short URL not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal Server Error', 'error': str(e)})
        }