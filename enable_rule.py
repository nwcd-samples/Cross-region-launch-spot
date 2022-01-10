#enable Cloudwatch rule
import boto3
client = boto3.client('events')
def lambda_handler(event, context):
   client.enable_rule(
    Name='EC2LaunchSuccessed'
)
