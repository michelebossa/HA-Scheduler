import sys
import os
import json
import psutil

FOLDER = "/share/ha-scheduler/"

# print("Recive", sys.argv[1])

input = sys.argv[1].split(":")
list = os.listdir(FOLDER)
reload = "false"
for file in list:
    if ".json" in file:
        filename = FOLDER + file
        with open(filename) as json_file:
            data = json.load(json_file)
        if data["friendly_name"] == input[0]:
            # print("trovato", data['entity_id'])
            if input[1] == "enable_on":
                data["enable"] = "true"
            if input[1] == "enable_off":
                data["enable"] = "false"
            with open(filename, "w") as outfile:
                json.dump(data, outfile)
            reload = "true"
if reload == "true":
    for process in psutil.process_iter():
#        if "/home/daemon.py" in process.cmdline():
#            print("Daemon Kill", process.pid)
#            os.system("kill " + str(process.pid))
#    os.system("python3 /home/daemon.py &")
        if "/home/app.py" in process.cmdline():
            print("App Kill", process.pid)
            os.system("kill " + str(process.pid))
    os.system("python3 /home/app.py &")
    print("App Start")
