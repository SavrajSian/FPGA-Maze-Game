import boto3
from botocore.exceptions import ClientError

def delete_kill(player, kill, dynamodb=None):
	if not dynamodb:
		dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

	table = dynamodb.Table('Kills')

	try:
		response = table.delete_item(Key={ 'player': player, 'kill': kill})
	except ClientError as e:
		if e.response['Error']['Code'] == "ConditionalCheckFailedException":
			print(e.response['Error']['Message'])
		else:
			raise
	else:
		return response

if __name__ == '__main__':
	player = int(input("player: "))
	kill = int(input("kill: "))
	delete_response = delete_kill(player, kill)
	if delete_response:
		print(f"Deleted {player} {kill}")