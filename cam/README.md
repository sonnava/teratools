# cam - Tools for Teradici Cloud Access Manager

## usermap.py
A simple script that reads a CSV file and creates assignments in *Teradici Cloud Access Manager* (https://cam.teradici.com/)
between users and remote workstations. CSV file should have 3 columns [userName, userGuid, machineName] and be comma-delimited.

### Requirements:
1. A Teradici Cloud Access Manager **Deployment Service Account**
Follow the steps (1-3) in this section to create one - https://cam.teradici.com/api/docs#section/Getting-Started/Prerequisites

2. Python3 and the following Python modules:
   - csv
   - pprint
   - requests

3. CSV file output from Active Directory with **[userName, userGuid, machineName] in this order** and **comma-delimited**.
