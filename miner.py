#!/usr/bin/env python3
import hashlib
import os
import socket
import sys
import time
import urllib.request
import json

soc = socket.socket()
soc.settimeout(10)

username = "0x0byalix"  # Edit this to your username, keep the quotes ..

def retrieve_server_ip():
    print("Retrieving Pool Address And Port")
    pool_obtained = False
    while not pool_obtained:
        try:
            serverip = ("https://server.duinocoin.com/getPool")
            # Loading pool address from API as json array
            poolInfo = json.loads(urllib.request.urlopen(serverip).read())
            
            global pool_address, pool_port
            # Line 1 = IP
            pool_address = poolInfo['ip']
            # Line 2 = port
            pool_port = poolInfo['port']
            pool_obtained =  True
        except:
            print("> Failed to retrieve Pool Address and Port, Retrying.")
            continue

retrieve_server_ip()
while True:
    try:
        # This section connects and logs user to the server
        soc.connect((str(pool_address), int(pool_port)))
        server_version = soc.recv(3).decode()  # Get server version
        print("Server is on version", server_version)

        # Mining section
        while True:
            # Send job request 
            soc.send(bytes(
                "JOB,"
                + str(username)
                + ",LOW",
                encoding="utf8"))

            # Receive work
            job = soc.recv(1024).decode().rstrip("\n")
            # Split received data to job and difficulty
            job = job.split(",")
            difficulty = job[2]
            
            hashingStartTime = time.time()
            base_hash = hashlib.sha1(str(job[0]).encode('ascii'))
            temp_hash = None
            
            for result in range(100 * int(difficulty) + 1):
                # Calculate hash with difficulty
                temp_hash =  base_hash.copy()
                temp_hash.update(str(result).encode('ascii'))
                ducos1 = temp_hash.hexdigest()

                # If hash is even with expected hash result
                if job[1] == ducos1:
                    hashingStopTime = time.time()
                    timeDifference = hashingStopTime - hashingStartTime
                    hashrate = result / timeDifference

                    # Send numeric result to the server
                    soc.send(bytes(
                        str(result)
                        + ","
                        + str(hashrate)
                        + ",Universal_Miner"
                        + "1.0",
                        encoding="utf8"))

                    feedback = soc.recv(1024).decode().rstrip("\n")

                    if feedback == "GOOD":
                        print("Accepted share",
                              result,
                              "Hashrate",
                              int(hashrate/1000),
                              "kH/s",
                              "Difficulty",
                              difficulty)
                        break

                    elif feedback == "BAD":
                        print("Rejected share",
                              result,
                              "Hashrate",
                              int(hashrate/1000),
                              "kH/s",
                              "Difficulty",
                              difficulty)
                        break

    except Exception as e:
        print("Error occured: " + str(e) + ", restarting in 5s.")
        retrieve_server_ip()
        time.sleep(5)
        os.execl(sys.executable, sys.executable, *sys.argv)
