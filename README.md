# Inteleccess-Assignment
Create cloud forma.on templates for provisioning the below resources
1) VPC with 2 private and public subnets. Please ensure that in the CFN you are
parameterizing and expor.ng values such as vpcid, vpc cidr, subne.ds, subnet cidrs
2) AWS VPN Client
3) RDS Database (Aurora MySQL Serverless)
Using the CFN templates created above, perform the below tasks

a) Deploy two vpc without overlapping CIDR using the above template (1) called as shared-
system-network and dev-system-network

b) Create VPC Peering between the two VPC’s created as part of step a.
c) Deploy AWS VPN client using the CFN stack created as part of step 2 on the shared
system network. Ensure that the VPN is able to connect to the resources that are
deployed on dev-system-network

d) Create and Deploy AWS RDS (Aurora Serverless DB) on private subnets of dev-system-
network

e) Install openvpn client and demo the connec.vity to RDS from development machine to
RDS without the use of SSH Tunnelling
