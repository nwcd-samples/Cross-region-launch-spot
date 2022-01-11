
import json
import boto3

ec2_client = boto3.client('ec2')
asg_client = boto3.client('autoscaling')

def lambda_handler(event, context):
    """
    :param event: SNS message triggered event
    :param context: AWS Lambda runtime context
    :return: the json like info includes the instance id and the termination time,
    """
    msg = event['Records'][0]['Sns']['Message']
    msg_json = json.loads(msg)
    id = msg_json['Trigger']['Dimensions'][0]['value']
    print("Instance id is " + str(id))

    # get the the instance info
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'instance-id',
                'Values': [str(id)]
            },
        ],
    )

    # print the ASG name 
    tags = response['Reservations'][0]['Instances'][0]['Tags']
    autoscaling_name = next(t["Value"] for t in tags if t["Key"] == "aws:autoscaling:groupName")
    print("Autoscaling name is - " + str(autoscaling_name))

    response = asg_client.client.terminate_instance_in_auto_scaling_group(
        InstanceIds=[
            str(id),
        ],
        AutoScalingGroupName=str(autoscaling_name),
        ShouldDecrementDesiredCapacity=True
    )

