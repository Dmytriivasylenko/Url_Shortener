import aws_cdk as core
import aws_cdk.assertions as assertions

from url_shortener.url_shortener_stack import UrlShortenerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in url_shortener/url_shortener_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = UrlShortenerStack(app, "url-shortener")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
