import boto3

ec2_client = boto3.client('ec2')

def get_all_subnets():
    subnets = []
    response = ec2_client.describe_subnets()
    for subnet in response['Subnets']:
        subnets.append(subnet['SubnetId'])
    return subnets

all_subnets = get_all_subnets()
print("All available subnets in all availability zones:")
print(all_subnets)
