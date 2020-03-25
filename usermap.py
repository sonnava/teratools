#!/usr/bin/env python
# 
# A simple script that reads a CSV file and creates assignments
# in Teradici Cloud Access Manager (https://cam.teradici.com/)
# between users and remote workstations. CSV file should
# have 3 columns [userName, userGuid, machineName] and be
# comma-delimited.
#

import requests
import pprint
import csv

#####
# Custom variables - Update these for your use
csv_file = 'usermap.csv' #should have 3 columns (output from AD): userName, userGuid, machineName
credentials = {"username":"-----","apiKey":"-----","deploymentId":"-----","tenantId":"-----"}
#####

# Teradici CAM API URL - do not modify
api_url = "https://cam.teradici.com/api/v1"

# Sign in and request session
request_body = dict(username=credentials.get('username'),password=credentials.get('apiKey'),tenantId=credentials.get('tenantId'))
response = requests.post("{}/auth/signin".format(api_url),json=request_body)

if not response.status_code == 200:
	raise Exception(response.text)
response_body = response.json()

auth_token = response_body.get('data').get('token')

# Create session object; all subsequent requests using the session
# will have the authorization header set
session = requests.Session()
session.headers.update({"Authorization": auth_token})

response = session.get("{}/deployments".format(api_url))

if not response.status_code == 200:
	raise Exception(response.text)
response_body = response.json()

deployment = response_body.get('data')[0]
deployment_id = deployment['deploymentId']

print('')
print('Deployement ID: ', deployment_id)

'''Function to check if workstation can be found in CAM and get machine_id'''
def get_machine_id( _deployment_id, _machine_name ):
	# Get machine_id with machine_name
	params = {'limit': 1, 'deploymentId': _deployment_id, 'machineName': _machine_name}
	response = session.get("{}/machines".format(api_url), params=params)

	if not response.status_code == 200:
		print('Error: get_machine_id output:', response.text)
		machine_id = None
	if response.json().get('total') == 0:
		print('Error: get_machine_id output:', response.text)
		machine_id = None
	else:
		response_body = response.json()
		machine = response_body.get('data')[0]
		machine_id = machine['machineId']

	return machine_id;

'''Function to check if user can be found in CAM'''
def user_exists( _deployment_id, _user_guid ):
	# Get list of users with user_guid
	params = {'limit': 1, 'offset': 0, 'deploymentId': _deployment_id, 'userGuid': _user_guid }
	response = session.get("{}/machines/entitlements/adusers?enabled=true".format(api_url), params=params)

	if not response.status_code == 200:
		print('Error: user_exists output:', response.text)
		return False;
	if response.json().get('total') == 0:
		print('Error: user_exists output:', response.text)
		return False;
	else:
		response_body = response.json()
		ad_users = response_body.get('data')

	if ad_users:
		user_guid = ad_users[0]['userGuid']
		return True;
	else:
		return False;

'''Function to check if entitlement between user and workstation can be found in CAM'''
def entitlement_exists( _deployment_id, _user_guid, _machine_id ):
	# Get list of entitlements(mapping) with user_guid and machine_id
	params = {'limit': 1, 'offset': 0, 'deploymentId': _deployment_id, 'userGuid': _user_guid, 'machineId': _machine_id }
	response = session.get("{}/machines/entitlements".format(api_url), params=params)

	if not response.status_code == 200:
		print('Error: entitlement_exists output:', response.text)
		return True;
	if response.json().get('total') == 0:
		return False;
	else:
		response_body = response.json()
		entitlement = response_body.get('data')
		print('Error: entitlement_exists output: entitlementId', entitlement[0]['entitlementId'])
		return True;

def assign_machine( _deployment_id, _user_guid, _machine_id ):
	# Assign Users to Workstations (create entitlement)
	body = dict(
    	deploymentId=_deployment_id,
    	machineId=_machine_id,
    	userGuid=_user_guid,
	)

	print('Assigning ', machine_name, ' to ', user_name, '.')
	response = session.post("{}/machines/entitlements".format(api_url), json=body)

	if not response.status_code == 201:
		print('Error: assign_machine output:', response.text)
	else:
		response_body = response.json()
		entitlement = response_body.get('data')
	return;


'''Read the CSV input file for user to workstation mapping '''
with open(csv_file) as csvfile:
    next(csvfile) # ignore header (comment this line if your csv does not have a header row)
    usermap = [ row.strip().split(',') for row in csvfile]

for userrow in usermap:

	user_name = userrow[0]
	user_guid = userrow[1]
	machine_name = userrow[2]

	print('')
	print('Trying to assign', machine_name, 'to', user_name, '...')
	machine_id = get_machine_id( deployment_id, machine_name );
	if not machine_id is None:
		if user_exists( deployment_id, user_guid ):
			if not entitlement_exists( deployment_id, user_guid, machine_id ):
				assign_machine( deployment_id, user_guid, machine_id);
				print('Success: workstation',machine_name, 'has been assigned to user', user_name)
			else:
				print('Error: workstation', machine_name, 'is likely already assigned to user', user_name)
		else:
			print('Error: user', user_name, 'could not be found in CAM')
	else:
		print('Error: workstation', machine_name, 'could not be found in CAM')
