import boto3
ec2_client = boto3.client('ec2')
print('Subnet_ID\tSubnet_Name')
print('-----------------------------')
sn_all = ec2_client.describe_subnets()

for sn in sn_all['Subnets'] :
    print(sn['SubnetId'], end='')
    for tag in sn['Tags']:
        if tag['Key'] == 'Name':
            print('\t' + tag['Value'])
