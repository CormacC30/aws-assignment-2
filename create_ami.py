import boto3
import webbrowser
import time
import datetime
import json
import random
import string
import subprocess

ec2 = boto3.resource('ec2')
s = [] # the list of instance names

current_time = datetime.datetime.now()

formatted_time = current_time.strftime('%Y-%m-%d-%H-%M-%S') # formatting the date time string

key_name = input('Please Enter Your Key Name:\n')
security_group_id = 'sg-0a3ae400e0e514dc4'

print ("All instances:")
for inst in ec2.instances.all():

# list of all the current instances:
    print (inst.id, inst.state)
            
new_instance_name = f'Master web server instance {formatted_time}' # gives the new instance an auto-incremented name
            
new_instances = ec2.create_instances(
    ImageId='ami-0277155c3f0ab2930',
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.nano',
    SecurityGroupIds=[ security_group_id ], # security group
    TagSpecifications=[ # tag: instance name
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': new_instance_name,
                },
            ]
        },
    ],
    
    #user data to create apache web server
    ### CHANGED SOME USER DATA
    UserData="""#!/bin/bash
            yum update -y
            yum install httpd -y
            systemctl enable httpd
            systemctl start httpd
            echo '<!DOCTYPE html>' > index.html 
            echo '<body>' >> index.html
            TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
            echo '<h1>Welcome to DevOps, HDip CS 2024, Assignment 2</h1><br>' >> index.html
            echo '<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Devops-toolchain.svg/640px-Devops-toolchain.svg.png" alt="Dev Ops Image">' >> index.html
            echo '<h2>See instance metadata below: </h2><br>' >> index.html
            echo '<p>Private IP Address: </p>' >> index.html
            echo $(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/local-ipv4) >> index.html
            echo '<br><p>availability zone: </p>' >> index.html
            echo $(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/placement/availability-zone) >> index.html
            echo 'Instance Type: '
            echo $(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://latest/meta-data/instance-type) >> index.html
            echo '<br><p>Public IP Address: </p>' >> index.html
            echo $(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/public-ipv4) >> index.html
            echo '<br><p>AMI ID: </p>' >> index.html
            echo $(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/ami-id) >> index.html
            echo '<br><p>Security Groups: </p>' >> index.html
            echo $(curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/security-groups) >> index.html
            echo '</body>' >> index.html
            cp index.html /var/www/html/index.html
            """,
    KeyName=key_name
    )

instance = new_instances[0]
instance_id = new_instances[0].instance_id # INSTANCE ID
    
print (f'Your New EC2 instance id is: {instance.id}')
print (f'Your new EC2 instance name is {new_instance_name}')
# uses waiter method to wait until the instance is in running state
print ("Instance Pending, please wait... ")
instance.wait_until_running()
print ("Instance Running")
instance.reload()
ip_address = instance.public_ip_address

print(f"The IP address of this instance is: {ip_address}")
print("Waiting for your apache web page to become available...")
time.sleep(30)
print("""
   _________________________________________
   
   ---------Opening EC2 Web page...---------
   _________________________________________
   
   """)    
webbrowser.open_new_tab(f"http://{ip_address}")

###NEW CODE FOR STOPPING AND CREATING THE IMAGE
ec2_client = boto3.client('ec2')

# Stop the instance
ec2_client.stop_instances(InstanceIds=[instance_id])
waiter = ec2_client.get_waiter('instance_stopped')
print("Waiting for the instance to stop...")
waiter.wait(InstanceIds=[instance_id])
print("Instance stopped.")

ami_name = f'Master Web Server {formatted_time}'
ami_description = f'Custom AMI for devops assignment 2 created on: {formatted_time}'

# Create the AMI
response = ec2_client.create_image(
    InstanceId=instance_id,
    Name=ami_name,
    Description=ami_description,
    NoReboot=True  # No need to reboot instance for AMI creation
)
ami_id = response['ImageId']
print(f"AMI '{ami_name}' (ID: {ami_id}) creation initiated.")

# Wait for AMI creation to complete
print("Waiting for the AMI to become available...")
waiter = ec2_client.get_waiter('image_available')
waiter.wait(ImageIds=[ami_id])
print(f"AMI '{ami_name}' (ID: {ami_id}) is now available.")

# Terminate the instance
ec2_client.terminate_instances(InstanceIds=[instance_id])
print("Instance terminated.")




