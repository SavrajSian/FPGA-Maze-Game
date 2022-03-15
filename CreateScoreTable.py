import boto3
from pprint import pprint
##creating the table
def create_score_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',region_name='us-east-1')

    table = dynamodb.create_table(
        TableName='Scores',
        KeySchema=[
            {
                'AttributeName': 'Username',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'Score',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'Username',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'Score',
                'AttributeType': 'N'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 100,
            'WriteCapacityUnits': 100
        }
    )
    return table
##inseting item into table
def put_movie(Username, Score, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('create_score_table')
    response = table.put_item(
       Item={
            'Username': Username,
            'Score': Score,
        }
    )
    return response


if __name__ == '__main__':
    score_table = create_score_table()
    print("Table status:", score_table.table_status)
    ########## inserting now
    while (True):
        movie_resp = put_movie("FPGA 1", 40)
    print("Put movie succeeded:")
    pprint(movie_resp)
