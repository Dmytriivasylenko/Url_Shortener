#!/usr/bin/env python3
import os
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    Stack,
)

class UrlShortenerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Creation DynamoDB Table

        table = dynamodb.Table(self, 'UrlShortenerTable',
                               partition_key=dynamodb.Attribute(name='short_key', type=dynamodb.AttributeType.STRING)
                               )

        # Create Lambda for Short URL
        shorten_lambda = _lambda.Function(self, 'ShortenLambda',
                                          runtime=_lambda.Runtime.PYTHON_3_9,
                                          handler='url_shortener.shorten_url',
                                          code=_lambda.Code.from_asset('lambda'),
                                          environment={
                                              'TABLE_NAME': table.table_name,
                                              'API_GATEWAY_URL': apigateway.RestApi(self, "DummyApi").url
                                          }
                                          )
        table.grant_read_write_data(shorten_lambda)

        # Lambda for Resolving URL
        resolve_lambda = _lambda.Function(self, 'resolve_url.resolve_url',
                                          runtime=_lambda.Runtime.PYTHON_3_9,
                                          handler='resolve_url.resolve_url',
                                          code=_lambda.Code.from_asset('lambda'),
                                          environment={
                                              'TABLE_NAME': table.table_name,
                                          }
        )
        table.grant_read_data(resolve_lambda)


        # API Gateway
        api = apigateway.RestApi(self, 'UrlShortenerApi', rest_api_name='URL Shortener Service')

        # POST /shorten
        shorten_integration = apigateway.LambdaIntegration(shorten_lambda)
        api.root.add_resource('shorten').add_method('POST', shorten_integration,
                                                    authorization_type=apigateway.AuthorizationType.NONE)

        # GET /{shortCode}
        url_resource = api.root.add_resource('{shortCode}')
        resolve_integration = apigateway.LambdaIntegration(resolve_lambda)
        url_resource.add_method('GET', resolve_integration,
                                authorization_type=apigateway.AuthorizationType.NONE)


app = cdk.App()
UrlShortenerStack(app, "UrlShortenerStack", env=cdk.Environment(account='670726858704', region='eu-north-1'))

