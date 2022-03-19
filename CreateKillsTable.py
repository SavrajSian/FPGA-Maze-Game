import boto3

def create_kills_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',region_name='us-east-1')

    table = dynamodb.create_table(
        TableName='Kills',
        KeySchema=[
            {
                'AttributeName': 'player',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'kills',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'player',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'kills',
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
    kills_table = create_kills_table()
    print("Table status:", kills_table.table_status)
