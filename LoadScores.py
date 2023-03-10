import boto3
from boto3.dynamodb.conditions import Key


def query_scores(player, dynamodb=None):
	if not dynamodb:
		dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

	table = dynamodb.Table('Scores')

	# Expression attribute names can only reference items in the projection expression.
	response = table.query(KeyConditionExpression=Key('player').eq(player), ScanIndexForward=False)
	return response['Items']

def get_scores ():
	scores_resp = []
	scores_list = []
	print(f"Scores of all players:")
	for i in range(4):
		scores_resp.append(query_scores(i))
	for partition in scores_resp:
		for entry in partition:
			scores_list.append([int(entry['player']), int(entry['score']), entry['datetime']])
	sorted_scores = sorted(scores_list, key=lambda x: x[1], reverse=True)
	return sorted_scores[0:5]

if __name__ == "__main__":
	get_scores()