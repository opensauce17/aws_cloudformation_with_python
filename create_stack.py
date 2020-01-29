#!/usr/bin/env python

import boto3
import json
import argparse
from urllib.parse import parse_qs
from datetime import datetime


# Colors for printing
class bcolors:
    HEADER = '\033[95m'
    INFOBLUE = '\u001b[36m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

BANNER = r'''
 _  __          _                       __        ______  _  _   _____   ____  _             _
| |/ /   _ _ __| |_ ___  ___ _   _ ___  \ \      / /  _ \| || | |  ___| / ___|| |_ __ _  ___| | __
| ' / | | | '__| __/ _ \/ __| | | / __|  \ \ /\ / /| |_) | || |_| |_    \___ \| __/ _` |/ __| |/ /
| . \ |_| | |  | || (_) \__ \ |_| \__ \   \ V  V / |  __/|__   _|  _|    ___) | || (_| | (__|   <
|_|\_\__,_|_|   \__\___/|___/\__, |___/    \_/\_/  |_|      |_| |_|     |____/ \__\__,_|\___|_|\_\
                             |___/
'''


# FUNCTIONS
def make_kv_from_args(params_as_querystring, name_prefix="", use_previous=None):

    nvs = parse_qs(params_as_querystring)

    kv_pairs = []
    for key in nvs:
        kv = {
            "{0}Key".format(name_prefix):key,
            "{0}Value".format(name_prefix):nvs[key][0],
        }
        if use_previous != None:
            kv['UsePreviousValue'] = use_previous

        kv_pairs.append(kv)

    return kv_pairs

def date_diff_in_Seconds(dt2, dt1):
    timedelta = dt2 - dt1
    return timedelta.days * 24 * 3600 + timedelta.seconds

def stream_events(cf, stack_name):
    # Stream the status of the  stack creation events to console. Stream fail based on timestamp

    get_stack = cf.describe_stacks(
        StackName=stack_name
    )
    print(bcolors.OKGREEN + '[ OK ]  ' + bcolors.ENDC + 'Cloudformation Stack ' + args["name"] + ' State: ' +
          get_stack['Stacks'][0]['StackStatus'])
    print("\n")

    while True:
        events = cf.describe_stack_events(
            StackName=stack_name
        )
        get_stack = cf.describe_stacks(
            StackName=stack_name
        )
        event_output = events['StackEvents']
        stack_output = get_stack['Stacks']

        for i in stack_output:
            if i['StackStatus'] == 'CREATE_COMPLETE' or i['StackStatus'] == 'UPDATE_COMPLETE':
                print(bcolors.OKGREEN + '[ OK ]  ' + bcolors.ENDC + 'Cloudformation Stack ' + args["name"] + ' State: '
                      + i['StackStatus'])
                print("\n")
                print(bcolors.INFOBLUE + '[ INFO ] ' + bcolors.ENDC + 'Stack ' + args["name"] + ' completed')
                print("\n")
                exit()

        for i in event_output:
            if i['ResourceStatus'] == 'CREATE_FAILED' or i['ResourceStatus'] == 'UPDATE_FAILED':
                now = str(datetime.utcnow())
                now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S.%f')
                event_date = str(i['Timestamp']).strip('+00:00')
                event_date = datetime.strptime(event_date, '%Y-%m-%d %H:%M:%S.%f')
                date_compare = date_diff_in_Seconds(now, event_date)
                logical_id = i['LogicalResourceId']
                reason = i['ResourceStatusReason']
                if date_compare > 30:
                    pass
                else:
                    print(bcolors.FAIL + '[ FAIL ]  ' + bcolors.ENDC +
                          'Resource: ' + logical_id + ' ' + 'failed. Rollback initiated. Reason for failure: \n\n'
                          + reason)
                    print("\n")
                    exit()
# END FUNCTIONS

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--template", required=True,
                help="location of the template file")
ap.add_argument("-n", "--name", required=True,
                help="name of the stack")
ap.add_argument("-r", "--region", required=True,
                help="the aws region")
ap.add_argument("-p", "--params", type=str, required=False,
                help='the key value pairs for the parameters of the stack')
ap.add_argument("-u", "--update", type=str, required=False,
                help='use this argument only if the stack requires updates')
args = vars(ap.parse_args())

# open the template file and load it into a dictionary
with open(args["template"]) as template_file:
    data = json.load(template_file)

# initiate a json object to be loaded to the api
content = json.dumps(data)

# Display Template Information
print(BANNER)
print('\n')
print(bcolors.INFOBLUE + '[ INFO ] ' + bcolors.ENDC + 'Template Description: ' + data['Description'])
print('\n')
if args["update"] == "True" or args["update"] == "t" or args["update"] == "T":
    print(bcolors.INFOBLUE + '[ INFO ] ' + bcolors.ENDC + 'The following resources will be updated:')
    print('\n')
else:
    print(bcolors.INFOBLUE + '[ INFO ] ' + bcolors.ENDC + 'The following resources will be created:')
    print('\n')

resources = data['Resources']

resource_type = []
for key, val in resources.items():
    value = val
    v = value['Type']
    resource_type.append(v)

# Calculate amount of resources per resource
result = dict((i, resource_type.count(i)) for i in resource_type)

print('------------------------------------------------------')
print("| {:<7}|    {:<15}".format('Count','Resource Type'))
print('------------------------------------------------------')

for k, v in result.items():
    print("| {:<7}|    {:<15}".format(v, k))
    print('------------------------------------------------------')
    
print('\n')

if args["update"] == "True" or args["update"] == "t" or args["update"] == "T":
    answer = input(bcolors.WARNING + '[ WARNING ] ' + bcolors.ENDC + 'Continue with Stack Update? yes/no: ')
else:
    answer = input(bcolors.WARNING + '[ WARNING ] ' + bcolors.ENDC + 'Continue with Stack Creation? yes/no: ')

if answer == "yes" or answer == 'y':


    cf = boto3.client('cloudformation', region_name=args["region"])
    params = make_kv_from_args(args["params"], "Parameter", False)

    if args["update"] == "True" or args["update"] == "t" or args["update"] == "T":

        print('\n')
        print(bcolors.INFOBLUE + '[ INFO ] ' + bcolors.ENDC + 'Updating Stack {}'.format(args["name"]) + ' in the '
              + args["region"] + ' region' )
        print('\n')

    else:

        print('\n')
        print(bcolors.INFOBLUE + '[ INFO ] ' + bcolors.ENDC + 'Creating Stack {}'.format(args["name"]) + ' in the ' +
              args["region"] + ' region')
        print('\n')


    if args["update"] == "True" or args["update"] == "t" or args["update"] == "T":

        # make the api call to update the stack
        stack = cf.update_stack(
            StackName=args["name"],
            TemplateBody=content,
            Parameters=params,
            Capabilities=['CAPABILITY_IAM']
        )
        stream_events(cf, args["name"])
    else:
        # make the api call to create the stack
        stack = cf.create_stack(
            StackName=args["name"],
            TemplateBody=content,
            Parameters=params,
            Capabilities=['CAPABILITY_IAM']
        )
        stream_events(cf, args["name"])

elif answer == "no" or answer == 'n':
    print('\n')
    print(bcolors.FAIL + '[ CANCELLED ]' + bcolors.ENDC +  ' Creation of Cloudformation Stack ' + args["name"]
          + ' Cancelled ')
    print('\n')
