# awscli must be installed and configured with user auth

# "ssh-security-group" must be an existing security group that opens :22
# "wide-open" must be an existing IAM role that allows ec2-run-instances

# "--master-only" may be passed as an argument to forego creating a new slave image

. conf/ec2-init.conf

cp ec2-init/master-ec2-init ./master-ec2-init-tmp

sed -i "s/GIT_TOKEN=\"\"/GIT_TOKEN=\"$GIT_TOKEN\"/" master-ec2-init-tmp
sed -i "s/SLAVE_PASS=\"\"/SLAVE_PASS=\"$SLAVE_PASS\"/" master-ec2-init-tmp  

# spin up master instance, querying for InstanceId and assigning to variable "MASTER_ID"
MASTER_ID=$(aws ec2 run-instances --image-id ami-d732f0b7 --instance-type t2.micro --key-name david-kp \
--security-groups ssh-security-group --iam-instance-profile Name=wide-open --user-data master-ec2-init-tmp --query 'Instances[0].InstanceId')
# remove quotes
MASTER_ID=$(sed 's/\"//g' <<< $MASTER_ID)

# output of run-instances apparently comes a fraction of a second before an IP address is assigned
# such a usability
MASTER_ADDRESS=$(aws ec2 describe-instances --instance-id $MASTER_ID --query 'Instances[0].PublicIpAddress')
MASTER_ADDRESS=$(sed 's/\"//g' <<< $MASTER_ADDRESS)


rm master-ec2-init-tmp 

# begin spinup of slave with master IP address in-hand

if [ $1 != "--master-only" ]; then 
    cp ec2-init/slave-ec2-init ./slave-ec2-init-tmp

    sed -i "s/GIT_TOKEN=\"\"/GIT_TOKEN=\"$GIT_TOKEN\"/" slave-ec2-init-tmp
    sed -i "s/MASTER_ADDRESS=\"\"/MASTER_ADDRESS=\"$MASTER_ADDRESS\"/" slave-ec2-init-tmp
    sed -i "s/SLAVE_PASS=\"\"/SLAVE_PASS=\"$SLAVE_PASS\"/" slave-ec2-init-tmp

    SLAVE_ID=$(aws ec2 run-instances --image-id ami-d732f0b7 --instance-type t2.micro --key-name $AWS_KEYPAIR \
    --security-groups ssh-security-group --user-data slave-ec2-init-tmp --query 'Instances[0].InstanceId')
    SLAVE_ID=$(sed 's/\"//g' <<< $SLAVE_ID)

    aws ec2 create-image --instance-id $SLAVE_ID --name="SLAVE_AMI"
fi