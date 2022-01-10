#开启ohio的ASG
import boto3
client = boto3.client('autoscaling',region_name='us-east-2')
def lambda_handler(event, context):
   client.put_scaling_policy(
    AutoScalingGroupName='ohioASG',
    PolicyName="ohiospot"
    Enabled=True
)
