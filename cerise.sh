#!/bin/bash

# awscli must be installed and configured with user auth

# "ssh-security-group" must be an existing security group that opens :22
# "wide-open" must be an existing IAM role that allows ec2-run-instances

. conf/ec2-init.conf

# verify ec2-init.conf
if [ ! "$GIT_TOKEN" ] || [ ! "SLAVE_PASS" ]; then
    echo "Missing variable(s) in conf/ec2.init.conf."
    exit 1
fi 

aws sts get-caller-identity --output table  # simple check for aws configuration

if [ $? != 0 ]; then    # exit on non-zero exit status
    exit 1
else
    echo "Valid awscli configuration found!"
fi

# check for keypair from conf file
if [ ! "$AWS_KEYPAIR" ]; then
    echo "No keypair referenced in configuration file."
    if [ "$(ls *.pem)" ]; then  # check for keypair in current directory
        KP_ARRAY=($(ls *.pem))
        AWS_KEYPAIR=${KP_ARRAY[0]}
        echo "Using" $AWS_KEYPAIR
    else
        echo "Generating keypair..."    # else generate keypair with random name
        KP_RANDOM=$RANDOM
        aws ec2 create-key-pair --key-name cerise --query "KeyMaterial" --output text > $KP_RANDOM".pem"
        AWS_KEYPAIR=$KP_RANDOM".pem"
        echo "Using" $AWS_KEYPAIR        
fi

cp ec2-init/master-ec2-init ./master-ec2-init-tmp   # move barebones init to tmp file for staging

# replace empty variable assignments
sed -i "" -e "s/GIT_TOKEN=\"\"/GIT_TOKEN=\"$GIT_TOKEN\"/" master-ec2-init-tmp
sed -i "" -e "s/SLAVE_PASS=\"\"/SLAVE_PASS=\"$SLAVE_PASS\"/" master-ec2-init-tmp  

# spin up master instance, querying for InstanceId and assigning to variable "MASTER_ID"
echo "Spinning up master instance..."
MASTER_ID=$(aws ec2 run-instances --image-id ami-d732f0b7 --instance-type t2.micro --key-name $AWS_KEYPAIR \
--security-groups ssh-security-group --iam-instance-profile Name=wide-open --user-data file://master-ec2-init-tmp --query 'Instances[0].InstanceId' --output text)

# output of run-instances apparently comes a fraction of a second before an IP address is assigned
# such a usability
MASTER_ADDRESS=$(aws ec2 describe-instances --instance-id $MASTER_ID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
echo
echo "Master instance ID =" $MASTER_ID
echo "Master IP address = " $MASTER_ADDRESS
echo

rm master-ec2-init-tmp

echo "Checking for existing slave AMI..."   
# returns "None" if slave does not exist
SLAVE_EXISTS=$(aws ec2 describe-images --filters "Name=owner-id,Values=$(aws sts get-caller-identity --query Account --output text)" "Name=name,Values=SLAVE_AMI" --query Images[0].ImageId --output text)

# begin spinup of slave with master IP address in-hand
if [ "$SLAVE_EXISTS" = "None" ]; then 
    cp ec2-init/slave-ec2-init ./slave-ec2-init-tmp  
    
    sed -i "" -e "s/GIT_TOKEN=\"\"/GIT_TOKEN=\"$GIT_TOKEN\"/" slave-ec2-init-tmp
    sed -i "" -e "s/MASTER_ADDRESS=\"\"/MASTER_ADDRESS=\"$MASTER_ADDRESS\"/" slave-ec2-init-tmp
    sed -i "" -e "s/SLAVE_PASS=\"\"/SLAVE_PASS=\"$SLAVE_PASS\"/" slave-ec2-init-tmp

    echo "No existing AMI. Spinning up dummy slave instance..."
    SLAVE_ID=$(aws ec2 run-instances --image-id ami-d732f0b7 --instance-type t2.micro --key-name $AWS_KEYPAIR \
    --security-groups ssh-security-group --user-data file://slave-ec2-init-tmp --query 'Instances[0].InstanceId' --output text)
    SLAVE_ADDRESS=$(aws ec2 describe-instances --instance-id $SLAVE_ID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
    echo
    echo "Slave instance ID =" $SLAVE_ID
    echo "Slave IP address = " $SLAVE_ADDRESS
    echo
    echo "Waiting for instance up..."
    aws ec2 wait instance-running --instance-ids $SLAVE_ID  # blocks until instance state = running
    echo "Polling slave until SSH up..."
    until ssh -o "StrictHostKeyChecking no" ubuntu@$SLAVE_ADDRESS "ls /home/ubuntu/aws-init.log"; do
        sleep 3
    done 
    echo "Tailing log file..."
    # ssh + tail onto log file.  redirect to grep, blocking until completion.  output also tee'd to /dev/tty.
    grep -q 'Slave initialization complete.' <(ssh -o "StrictHostKeyChecking no" ubuntu@$SLAVE_ADDRESS "tail -f /home/ubuntu/aws-init.log" | tee /dev/tty)
    echo "Commiting slave instance to image..." # with dummy slave fully staged, commit to image for later use
    aws ec2 create-image --instance-id $SLAVE_ID --name="SLAVE_AMI" --output text
    rm slave-ec2-init-tmp
    echo "Waiting for image (this will take time)..."
    aws ec2 wait image-available --filters "Name=owner-id,Values=$(aws sts get-caller-identity --query Account --output text)" "Name=name,Values=SLAVE_AMI"
    echo "Terminating dummy slave..."
    aws ec2 terminate-instances --instance-ids $SLAVE_ID --output text
else
    echo "Slave image already exists.  Omitting slave spinup."
fi

echo "All tasks complete."