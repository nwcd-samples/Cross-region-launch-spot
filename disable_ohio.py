#关闭ohio的ASG
import boto3
client = boto3.client('autoscaling',region_name='us-east-2')
def lambda_handler(event, context):
   client.put_scaling_policy(
    AutoScalingGroupName='ohioASG',
    PolicyName="ohiospot"
    Enabled=False
)
   client.set_desired_capacity(
    AutoScalingGroupName='ohioASG',
    DesiredCapacity=0
)
   
