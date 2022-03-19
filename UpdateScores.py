import boto3
from datetime import datetime

def upload_score(player, score, datetime, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('Scores')
    response = table.put_item(
       Item={
            'player': player,
            'score': score,
            'datetime': datetime
        }
    )
    return response


def upload_scores (scores):
    date_time = datetime.now().isoformat()
    date = date_time.split('T')[0]
    time = date_time.split('T')[1].split(".")[0]
    date_string = date  + " " + time

    for i in range(4):
        resp = upload_score(i, scores[i], date_string)
        print(f"Uploading {i} {scores[i]} {date_string}")

if __name__ == "__main__":
    score1 = int(input("score 1: "))
    score2 = int(input("score 2: "))
    score3 = int(input("score 3: "))
    score4 = int(input("score 4: "))
    upload_scores([score1, score2, score3, score4])