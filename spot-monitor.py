import schedule
import time
import requests


def check_job():
    is_marked = requests.get('http://169.254.169.254/latest/meta-data/spot/termination-time')
    if is_marked.status_code != 404:
        send_notifications()


def send_notifications():
    print("SEND MESSAGE TO SNS") # Insert Your Code to Handle Interruption Here
  


if __name__ == "__main__":
    schedule.every(10).seconds.do(check_job)
    while True:
        schedule.run_pending()
        time.sleep(1)


def lambda_handler(event, context):
    """
    :param event: interruption acton Event send to AWS EventBridge which triggered AWS lambda 
    :param context: AWS Lambda runtime context
    :return: the json like info includes the instance id and the termination time,
    """
    # TODO implement
    info = "INSTANCE IS RUNNING AS EXPECTED"
    if event["detail"]["instance-action"] == "terminate":
        info = {
            "instance-id": event["detail"]["instance-id"],
            "instance_action": event["detail"]["instance_action"],
            "termination_time": event["time"]
        }
        send_notifications()

    return {
        'statusCode': 200,
        'body': json.dumps(info)
    }
