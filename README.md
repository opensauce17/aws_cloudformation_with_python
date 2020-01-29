# Cloudformation with Python 

This script reads a cloudformation template and applies it to the given AWS region. 


#### Requirements

1. AWS credentials configured in user home directory
2. Python 3
3. The following python libraries : 
	1. boto3
	2. json
	3. argparse
	4. urllib.parse
	
#### Usage

The scripts name is create_stack.py. Running `create_stack.py -h` will reveal the script help. 

`usage: create_stack.py [-h] -t TEMPLATE -n NAME -r REGION [-p PARAMS]
                       [-u UPDATE]`
 
`optional arguments:` 
  -h, --help            show this help message and exit
  -t TEMPLATE, --template TEMPLATE
                        location of the template file
  -n NAME, --name NAME  name of the stack
  -r REGION, --region REGION
                        the aws region
  -p PARAMS, --params PARAMS
                        the key value pairs for the parameters of the stack
  -u UPDATE, --update UPDATE
                        use this argument only if the stack requires updates 
                        
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
