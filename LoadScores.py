from pprint import pprint
import boto3
from boto3.dynamodb.conditions import Key


def query_and_project_movies(Username, score_range, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('Scores')
    print(f"load all scores and data")

    # Expression attribute names can only reference items in the projection expression.
    response = table.query(
        KeyConditionExpression=
             Key('Username').eq(Username) & Key('Score').between(score_range[0], score_range[1])
    )
    return response['Items']


if __name__ == '__main__':
    query_range = (0, 200)
    print(f"Scores of all balls "
          f"{query_range[0]} to {query_range[1]}")
    movies = query_and_project_movies("Ball 0" , query_range)
    for scores in movies:
        print(f"\n{scores['Username']} : {scores['Score']}")
