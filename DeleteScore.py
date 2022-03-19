import boto3
from botocore.exceptions import ClientError

def delete_score(player, score, dynamodb=None):
	if not dynamodb:
		dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

	table = dynamodb.Table('Scores')

	try:
		response = table.delete_item(Key={ 'player': player, 'score': score})
	except ClientError as e:
		if e.response['Error']['Code'] == "ConditionalCheckFailedException":
			print(e.response['Error']['Message'])
		else:
			raise
	else:
		return response

if __name__ == '__main__':
	player = int(input("player: "))
	score = int(input("score: "))
	delete_response = delete_score(player, score)
	if delete_response:
		print(f"Deleted {player} {score}")