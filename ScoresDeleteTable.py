import boto3

def delete_scores_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

    table = dynamodb.Table('Scores')
    table.delete()


if __name__ == '__main__':
    delete_scores_table()
    print("Scores table deleted.")
