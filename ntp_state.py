#####################################################
## cisco_load_config.py
## created by gdtlumauig 2026
#####################################################
from netmiko import ConnectHandler
from datetime import datetime
from netmiko.exceptions import NetMikoTimeoutException
from netmiko.exceptions import AuthenticationException
from netmiko.exceptions import SSHException
import os
import getpass
import csv
import os
import sys
import re


def parse_ntp(hostname,ntpconfig,ntpstatus):

    ntp_source = "None"
    ntp_servers = []
    timezone = "None"
    
    #Parsing hostname value
    hnmatch = re.search(r"^hostname (\S+)", hostname, re.MULTILINE)
    if hnmatch:
        hostvalue = hostname.group(1)
    
    #Parsing ntp source config
    nsmatch = re.search(r"^ntp source (\S+)", ntpconfig, re.MULTILINE)
    if nsmatch:
        ntp_source = nsmatch.group(1)
    
    #Parsing ntp server config
    for line in ntpconfig.splitlines():
        if line.startswith("ntp server"):
            parts = line.split()
            if len(parts) >= 3:
                ntp_servers.append(parts[2])
    
    #Parsing ntp timezone config
    tzmatch = re.search(r"^clock timezone (\S+)", ntpconfig, re.MULTILINE)
    if tzmatch:
        timezone = tzmatch.group(1)

   #Parsing ntp status output
    ntpstatus = ntpstatus.lower().strip()

    if "clock is synchronized" in ntpstatus:
        ntp_status = "Synchronized"
    else:
        ntp_status = "Unsynchronized"

    tzmatch = re.search(r"^clock timezone (\S+)", ntpconfig, re.MULTILINE)
    if tzmatch:
        timezone = tzmatch.group(1)


    return hostvalue,ntp_source,ntp_servers[0],ntp_servers[1],timezone,ntp_status



###MAIN

try:
    os.system('cls') 
    print("=====================================")
    print("Search NTP To Cisco Device")
    print("Created by G-Lumauig\n")
    print("\n=====================================")

    username = input("Enter your username: ")
    passwd = getpass.getpass("Enter your password: ")
    device_list = input("Enter the filename of the device list: ")

    ##error handling    
    try:
        dl_file = os.path.join("devicelist_folder",device_list)
        with open(dl_file,'r') as dev_list:
            devices = dev_list.readlines()
        
        for device in devices:
            try:
            ###Login to the device
                ntp_svr1= ""
                ntp_svr2=""
                tzone=""
                ntp_stat=""

                cisco_device = {
                    'device_type' : 'cisco_ios',
                    'host': device,
                    'username': username,
                    'password': passwd,
                }
            
                net_connect = ConnectHandler(**cisco_device)
                show_run_ntp_output = net_connect.send_command("show running-config | section ntp|clock timezone")
                show_ntp_stat_output = net_connect.send_command ("show ntp status | include Clock")
                show_run_hostname_output = net_connect.send_command ("show running-config | include hostname")
                hostname,ntp_source,ntp_svr1,ntp_svr2,tzone,ntp_stat = parse_ntp(show_run_hostname_output,show_run_ntp_output,show_ntp_stat_output)

            except AuthenticationException:
                print("Authentication error")
                hostname=device
                ntp_svr1= "NA-Autherr"
                ntp_svr2="NA-Autherr"
                tzone="NA-Autherr"
                ntp_stat="NA-Autherr"

            except NetMikoTimeoutException:
                hostname=device
                ntp_svr1= "NA-Unreachable"
                ntp_svr2="NNA-Unreachable"
                tzone="NNA-Unreachable"
                ntp_stat="NA-Unreachable"

            except Exception as e:
                print(f"An error occurred: {e}")
                hostname=device
                ntp_svr1= "NA-Err"
                ntp_svr2="NNA-Err"
                tzone="NNA-Err"
                ntp_stat="NA-Err"

            filename_csv = "ntp_status.txt"
            row_ntp_status = hostname+";"+ntp_source+";"+ntp_svr1+";"+ntp_svr2+";"+tzone+";"+ntp_stat
            with open(filename_csv,'w') as f_csv:
                f_csv.write (row_ntp_status)


    except FileNotFoundError:
        print(f"Command filename {dl_file} not found in load_config_folder")
        result = "File_Error"

except KeyboardInterrupt:
    print("\n=====================================")
    print("KeyboardInterrupt received. Exiting gracefully.")
    print("\n=====================================")



