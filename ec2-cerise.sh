# awscli must be installed and configured with user auth

# ssh-security-group must be an existing security group that opens :22
# this is necessary for scp and ssh access

# wide-open must be an existing security group that allows ec2-run-instances

. conf/ec2-init.conf

cp ec2-init/master-ec2-init ./master-ec2-init-tmp

sed -i "s/GIT_TOKEN = \"\"/GIT_TOKEN = \"$GIT_TOKEN\"/" master-ec2-init-tmp
sed -i "s/SLAVE_PASS = \"\"/SLAVE_PASS = \"$SLAVE_PASS\"/" master-ec2-init-tmp  
 

aws ec2-run-instances ami-d732f0b7 -t t2.micro -k $AWS_KEYPAIR -g ssh-security-group wide-open -f master-ec2-init-tmp

rm master-ec2-init-tmp 