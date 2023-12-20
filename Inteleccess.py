#VPC with 2 private and public subnets:
AWSTemplateFormatVersion: '2010-09-09'
Parameters:
  VpcCidr:
    Type: String
    Description: CIDR block for the VPC
  PublicSubnet1Cidr:
    Type: String
    Description: CIDR block for the first public subnet
  PublicSubnet2Cidr:
    Type: String
    Description: CIDR block for the second public subnet
  PrivateSubnet1Cidr:
    Type: String
    Description: CIDR block for the first private subnet
  PrivateSubnet2Cidr:
    Type: String
    Description: CIDR block for the second private subnet

Resources:
  MyVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: MyVPC

  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: !Ref PublicSubnet1Cidr
      MapPublicIpOnLaunch: true
      AvailabilityZone: us-east-1a
      Tags:
        - Key: Name
          Value: PublicSubnet1

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: !Ref PublicSubnet2Cidr
      MapPublicIpOnLaunch: true
      AvailabilityZone: us-east-1b
      Tags:
        - Key: Name
          Value: PublicSubnet2

  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: !Ref PrivateSubnet1Cidr
      AvailabilityZone: us-east-1a
      Tags:
        - Key: Name
          Value: PrivateSubnet1

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVPC
      CidrBlock: !Ref PrivateSubnet2Cidr
      AvailabilityZone: us-east-1b
      Tags:
        - Key: Name
          Value: PrivateSubnet2

Outputs:
  VpcId:
    Value: !Ref MyVPC
    Export:
      Name: VpcId
  PublicSubnet1Id:
    Value: !Ref PublicSubnet1
    Export:
      Name: PublicSubnet1Id
  PublicSubnet2Id:
    Value: !Ref PublicSubnet2
    Export:
      Name: PublicSubnet2Id
  PrivateSubnet1Id:
    Value: !Ref PrivateSubnet1
    Export:
      Name: PrivateSubnet1Id
  PrivateSubnet2Id:
    Value: !Ref PrivateSubnet2
    Export:
      Name: PrivateSubnet2Id
#AWS VPN Client:
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyVPNClients:
    Type: AWS::EC2::ClientVpnEndpoint
    Properties:
      AuthenticationOptions:
        - Type: certificate-authentication
          MutualAuthentication:
            ClientRootCertificateChainArn: "arn:aws:acm:region:account-id:certificate/certificate-id"
      ClientCidrBlock: "10.0.0.0/16"
      ConnectionLogOptions:
        Enabled: true
        CloudwatchLogGroup: "/aws/vpn-logs"
        CloudwatchLogStream: "MyVPNLogStream"
      ServerCertificateArn: "arn:aws:acm:region:account-id:certificate/certificate-id"
      Description: "My VPN Connection"
      TransportProtocol: "udp"
      SplitTunnel: true

AWSTemplateFormatVersion: '2010-09-09'
Parameters:
  DBUsername:
    Type: String
    Description: Master username for the RDS instance
  DBPassword:
    Type: String
    NoEcho: true
    Description: Master password for the RDS instance
#RDS Database (Aurora MySQL Serverless):
Resources:
  MyAuroraServerlessDB:
    Type: AWS::RDS::DBCluster
    Properties:
      Engine: aurora
      EngineMode: serverless
      MasterUsername: !Ref DBUsername
      MasterUserPassword: !Ref DBPassword
      BackupRetentionPeriod: 7
      ScalingConfiguration:
        AutoPause: true
        MinCapacity: 2
        MaxCapacity: 16
        SecondsUntilAutoPause: 300
        AutoPause: true
      Tags:
        - Key: Name
          Value: MyAuroraServerlessDB

# Deploy two VPCs without overlapping CIDRs:
aws cloudformation create-stack --stack-name SharedSystemNetwork --template-body file://vpc-template.yaml --parameters ParameterKey=VpcCidr,ParameterValue=10.0.0.0/16 ParameterKey=PublicSubnet1Cidr,ParameterValue=10.0.1.0/24 ParameterKey=PublicSubnet2Cidr,ParameterValue=10.0.2.0/24 ParameterKey=PrivateSubnet1Cidr,ParameterValue=10.0.3.0/24 ParameterKey=PrivateSubnet2Cidr,ParameterValue=10.0.4.0/24
aws cloudformation create-stack --stack-name DevSystemNetwork --template-body file://vpc-template.yaml --parameters ParameterKey=VpcCidr,ParameterValue=192.168.0.0/16 ParameterKey=PublicSubnet1Cidr,ParameterValue=192.168.1.0/24 ParameterKey=PublicSubnet2Cidr,ParameterValue=192.168.2.0/24 ParameterKey=PrivateSubnet1Cidr,ParameterValue=192.168.3.0/24 ParameterKey=PrivateSubnet2Cidr,ParameterValue=192.168.4.0/24

#Create VPC Peering between the two VPCs:
aws ec2 create-vpc-peering-connection --vpc-id vpc-id-of-shared-system-network --peer-vpc-id vpc-id-of-dev-system-network

#Deploy AWS VPN client on shared-system-network:
aws cloudformation create-stack --stack-name VPNClientStack --template-body file://vpn-client-template.yaml

#Create and Deploy AWS RDS on private subnets of dev-system-network:
aws cloudformation create-stack --stack-name RDSStack --template-body file://rds-template.yaml --parameters ParameterKey=DBUsername,ParameterValue=your-db-username ParameterKey=DBPassword,ParameterValue=your-db-password
