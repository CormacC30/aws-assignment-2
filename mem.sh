#!/bin/bash
TOKEN=`curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`

INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id)

USEDMEMORY=$(free -m | awk 'NR==2{printf "%.2f", $3*100/$2 }')
TCP_CONN=$(netstat -an | wc -l)
TCP_CONN_PORT_80=$(netstat -an | grep 80 | wc -l)
IO_WAIT=$(iostat | awk 'NR==4 {print $5}')
DISK_READ=$(iostat -d | awk 'NR==4 {print $3}')
DISK_WRITE=$(iostat -d | awk 'NR==4 {print $4}')
CPU_UTIL=$(sar -u 1 1 | grep "Average" | awk '{print 100 - $NF}')

aws cloudwatch put-metric-data --region us-east-1 --metric-name memory-usage --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $USEDMEMORY
aws cloudwatch put-metric-data --region us-east-1 --metric-name Tcp_connections --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $TCP_CONN
aws cloudwatch put-metric-data --region us-east-1 --metric-name TCP_connection_on_port_80 --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $TCP_CONN_PO>
aws cloudwatch put-metric-data --region us-east-1 --metric-name IO_WAIT --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $IO_WAIT
aws cloudwatch put-metric-data --region us-east-1 --metric-name DiskRead --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $DISK_READ
aws cloudwatch put-metric-data --region us-east-1 --metric-name DiskWrite --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $DISK_WRITE
aws cloudwatch put-metric-data --region us-east-1 --metric-name CPUUtilization --dimensions Instance=$INSTANCE_ID --namespace "Custom" --value $CPU_UTIL

