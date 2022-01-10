#disable Cloudwatch rule
import boto3
client = boto3.client('events')
def lambda_handler(event, context):
   client.disable_rule(
    Name='EC2LaunchFail'
)
