import boto3

def create_score_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',region_name='us-east-1')

    table = dynamodb.create_table(
        TableName='Scores',
        KeySchema=[
            {
                'AttributeName': 'player',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'score',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'player',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'score',
                'AttributeType': 'N'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 100,
            'WriteCapacityUnits': 100
        }
    )
    return table


if __name__ == '__main__':
    score_table = create_score_table()
    print("Table status:", score_table.table_status)
