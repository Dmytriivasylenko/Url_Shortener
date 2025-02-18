import boto3
import json
import random
import string
import os
import time
from urllib.parse import urlparse

from boto3.dynamodb import table


def generate_short_key(length=6):
    """Generates a random short key."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def is_valid_url(long_url):
    """Checks if a URL is valid."""
    try:
        result = urlparse(long_url)
        return result.scheme in ["http", "https"] and bool(result.netloc)
    except Exception:
        return False

def shorten_url(event, context):
    try:
        body = json.loads(event['body'])
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid JSON in request body'})
        }

    if 'long_url' not in body:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing "long_url" in request body'})
        }

    long_url = body['long_url']

    # Налаштування часу дії URL (TTL) – наприклад, 5 хвилин
    ttl_seconds = 5 * 60  # Наприклад, 5 хвилин
    expire_at = int(time.time()) + ttl_seconds  # Поточний час + 5 хвилин

    # Створення короткого URL
    short_key = generate_short_key()

    # Вставка даних в таблицю DynamoDB
    table.put_item(
        Item={
            'short_key': short_key,
            'long_url': long_url,
            'usage_count': 0,  # Початкова кількість використань
            'max_usage': 2,  # Максимальна кількість використань
            'expire_at': expire_at  # Час, коли посилання буде видалено
        },
        ConditionExpression='attribute_not_exists(short_key)'  # Перевірка на унікальність short_key
    )

    api_gateway_url = os.environ['API_GATEWAY_URL']
    return {
        'statusCode': 200,
        'body': json.dumps({'short_url': f'{api_gateway_url}/{short_key}'})
    }