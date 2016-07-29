#!/bin/bash

# awscli must be installed and configured with user auth

# "ssh-security-group" must be an existing security group that opens :22
# "wide-open" must be an existing IAM role that allows ec2-run-instances

. conf/ec2-init.conf

# verify ec2-init.conf
if [ ! "$GIT_TOKEN" ] || [ ! "SLAVE_PASS" ] || [ ! "AWS_KEYPAIR" ]; then
    echo "Missing variable(s) in conf/ec2.init.conf."
    exit 1
fi 

aws sts get-caller-identity --output table

if [ $? != 0 ]; then
    exit 1
else
    echo "Valid awscli configuration found!"
fi

cp ec2-init/master-ec2-init ./master-ec2-init-tmp

sed -i "" -e "s/GIT_TOKEN=\"\"/GIT_TOKEN=\"$GIT_TOKEN\"/" master-ec2-init-tmp
sed -i "" -e "s/SLAVE_PASS=\"\"/SLAVE_PASS=\"$SLAVE_PASS\"/" master-ec2-init-tmp  

# spin up master instance, querying for InstanceId and assigning to variable "MASTER_ID"
echo "Spinning up master instance..."
MASTER_ID=$(aws ec2 run-instances --image-id ami-d732f0b7 --instance-type t2.micro --key-name $AWS_KEYPAIR \
--security-groups ssh-security-group --iam-instance-profile Name=wide-open --user-data master-ec2-init-tmp --query 'Instances[0].InstanceId' --output text)

# output of run-instances apparently comes a fraction of a second before an IP address is assigned
# such a usability
aws ec2 wait instance-running --instance-ids $MASTER_ID
MASTER_ADDRESS=$(aws ec2 describe-instances --instance-id $MASTER_ID --query 'Instances[0].PublicIpAddress' --output text)
echo "Master IP address = " $MASTER_ADDRESS

rm master-ec2-init-tmp 

echo "Checking for existing slave AMI..."
SLAVE_EXISTS=$(aws ec2 describe-images --filters "Name=owner-id,Values=$(aws sts get-caller-identity --query Account --output text)" "Name=name,Values=SLAVE_AMI" --query Images[0].ImageId --output text)

# begin spinup of slave with master IP address in-hand
if [ "$SLAVE_EXISTS" = "None" ]; then 
    cp ec2-init/slave-ec2-init ./slave-ec2-init-tmp

    sed -i "" -e "s/GIT_TOKEN=\"\"/GIT_TOKEN=\"$GIT_TOKEN\"/" slave-ec2-init-tmp
    sed -i "" -e "s/MASTER_ADDRESS=\"\"/MASTER_ADDRESS=\"$MASTER_ADDRESS\"/" slave-ec2-init-tmp
    sed -i "" -e "s/SLAVE_PASS=\"\"/SLAVE_PASS=\"$SLAVE_PASS\"/" slave-ec2-init-tmp

    echo "No existing AMI. Spinning up dummy slave instance..."
    SLAVE_ID=$(aws ec2 run-instances --image-id ami-d732f0b7 --instance-type t2.micro --key-name $AWS_KEYPAIR \
    --security-groups ssh-security-group --user-data slave-ec2-init-tmp --query 'Instances[0].InstanceId' --output text)

    echo "Waiting for slave init to complete..."
    aws ec2 wait instance-status-ok --instance-ids $SLAVE_ID
    echo "Commiting slave instance to image..." 
    aws ec2 create-image --instance-id $SLAVE_ID --name="SLAVE_AMI"
    echo "Waiting for image (this will take time)..."
    aws ec2 wait image-available --filters "Name=owner-id,Values=$(aws sts get-caller-identity --query Account --output text)" "Name=name,Values=SLAVE_AMI"
    echo "Terminating dummy slave..."
    aws ec2 terminate-instances --instance-ids $SLAVE_ID
else
    echo "Slave image already exists.  Omitting slave spinup."
fi

echo "All tasks complete."
