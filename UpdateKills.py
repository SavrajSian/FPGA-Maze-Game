import boto3
from datetime import datetime

def upload_kill(player, kill, datetime, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('Kills')
    response = table.put_item(
       Item={
            'player': player,
            'kills': kill,
            'datetime': datetime
        }
    )
    return response


def upload_kills (kills):
    date_time = datetime.now().isoformat()
    date = date_time.split('T')[0]
    time = date_time.split('T')[1].split(".")[0]
    date_string = date  + " " + time

    for i in range(4):
        resp = upload_kill(i, kills[i], date_string)
        print(f"Uploading {i} {kills[i]} {date_string}")

if __name__ == "__main__":
    kill1 = int(input("kill 1: "))
    kill2 = int(input("kill 2: "))
    kill3 = int(input("kill 3: "))
    kill4 = int(input("kill 4: "))
    upload_kills([kill1, kill2, kill3, kill4])