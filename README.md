# Cloudformation with Python 

This script reads a cloudformation template and applies it to the given AWS region. 


#### Requirements

1. AWS credentials configured in user home directory as ~/.aws/credentials with format: 
```
[default]
aws_access_key_id = KEY_ID_HERE
aws_secret_access_key = ACCESS_KEY_HERE
```

2. Python 3
3. The following python libraries : 
	1. boto3
	2. json
	3. argparse
	4. urllib.parse
	
#### Usage

The scripts name is create_stack.py. Running `create_stack.py -h` will reveal the script help. 

                        
<a href="#"><img src="https://i.ibb.co/4mbLdYd/aws-cf-help2.png" alt="aws-cf-help2" border="0" /></a>

The script takes 4 arguments:

TEMPLATE
NAME
REGION
PARAMS
UPDATE

The PARAMS argument is optional since defaults can be configured in the template. When including the params option in the script execution use the following format: 

-p "Keyname=keyvalue&Keyname=keyvalue"
eg.
-p "DBUser=wp_db_master&DBPassword=S0m3Pa33W0rd"

The UPDATE argument is optional and when invoked takes any one of these: True, T or t
