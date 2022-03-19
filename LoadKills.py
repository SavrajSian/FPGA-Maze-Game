import boto3
from boto3.dynamodb.conditions import Key


def query_kills(player, dynamodb=None):
	if not dynamodb:
		dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

	table = dynamodb.Table('Kills')

	# Expression attribute names can only reference items in the projection expression.
	response = table.query(KeyConditionExpression=Key('player').eq(player), ScanIndexForward=False)
	return response['Items']

def get_kills ():
	kills_resp = []
	kills_list = []
	print(f"Kills of all players:")
	for i in range(4):
		kills_resp.append(query_kills(i))
	for partition in kills_resp:
		for entry in partition:
			kills_list.append([int(entry['player']), int(entry['kills']), entry['datetime']])
	sorted_kills = sorted(kills_list, key=lambda x: x[1], reverse=True)
	return sorted_kills[0:5]

if __name__ == "__main__":
	get_kills()