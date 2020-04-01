import requests 
from datetime import datetime, timezone, timedelta
import time
import json
import os
import logging

scheduled = []
scheduled_today = []
next_setting = ""
next_rising = ""
FOLDER = "/share/ha-scheduler/"

def load_scheduled():
    list = os.listdir(FOLDER)
    for file in list:
       if ".json" in file:
         filename = FOLDER + file
         with open(filename) as json_file:
           sche = json.load(json_file)
           if sche["enable"] == "true":
              scheduled.append(sche)

def get_sun():
    URL = "http://hassio/homeassistant/api/states/sun.sun"
               
    # defining a params dict for the parameters to be sent to the API 
    Auth = 'Bearer ' + SUPERVISOR_TOKEN
    headers = {'content-type': 'application/json', 'Authorization' : Auth } 
          
    # sending get request and saving the response as response object 
    response = requests.get(url = URL, headers=headers) 
    json_data = response.json()["attributes"]
    global next_setting
    global next_rising
    next_setting = datetime.strptime(json_data["next_setting"], '%Y-%m-%dT%H:%M:%S%z')     
    next_setting = next_setting.replace(tzinfo=timezone.utc).astimezone(tz=None)    
    next_rising = datetime.strptime(json_data["next_rising"], '%Y-%m-%dT%H:%M:%S%z')      
    next_rising = next_rising.replace(tzinfo=timezone.utc).astimezone(tz=None)

    filename = FOLDER + "sun.sun"
    sun = { 
            "sunrise" : next_rising.strftime("%H:%M:%S"),
            "sunset" : next_setting.strftime("%H:%M:%S")
    }
    with open(filename, 'w') as outfile:
         json.dump(sun, outfile)
        
    #print("Sunset", next_setting.strftime("%H:%M:%S") , "Sunrise", next_rising.strftime("%H:%M:%S") )
    mes = "Sunset " + next_setting.strftime("%H:%M:%S") + " Sunrise " + next_rising.strftime("%H:%M:%S")
    logging.info( mes )
    
def call_service(dominio,id,action):
    URL = "http://hassio/homeassistant/api/services/" + dominio + "/turn_" + action
               
    # defining a params dict for the parameters to be sent to the API 
    Auth = 'Bearer ' + SUPERVISOR_TOKEN
    data = {'entity_id': id }
    #print(Auth)
    headers = {'content-type': 'application/json', 'Authorization' : Auth } 
          
    # sending get request and saving the response as response object 
    response = requests.post(url = URL, headers=headers,json=data)      
    mes = str(id) + " Turn " + str(action)
    logging.info( mes )


def get_schedule_today( ):
    global scheduled_today 
    scheduled_today = []
    now = datetime.now()
    day = now.isoweekday()
    for sche in scheduled:
        time_sched_on = ""
        time_sched_off = ""
        name = "ON_" + str(day)
        time_sched_on = sche[name]
        name = "OFF_" + str(day)
        time_sched_off = sche[name]
        if time_sched_on != "" or time_sched_off != "":
           if time_sched_on != "" and "sunrise" in time_sched_on:
             if "+" in time_sched_on or "-" in time_sched_on:
               if "+" in time_sched_on:
                 tmp = time_sched_on.split("+")
                 second = int(tmp[1]) 
                 data = next_rising + timedelta(seconds=second)
                 time_sched_on = data.strftime("%H:%M:%S")
               else:
                 tmp = time_sched_on.split("-")
                 second = int(tmp[1]) 
                 data = next_rising - timedelta(seconds=second)                 
                 time_sched_on = data.strftime("%H:%M:%S")
             else:
                 time_sched_on = next_rising.strftime("%H:%M:%S")
                 
           if time_sched_on != "" and "sunset" in time_sched_on:
             if "+" in time_sched_on or "-" in time_sched_on:
               if "+" in time_sched_on:
                 tmp = time_sched_on.split("+")
                 second = int(tmp[1]) 
                 data = next_setting + timedelta(seconds=second)
                 time_sched_on = data.strftime("%H:%M:%S")
               else:
                 tmp = time_sched_on.split("-")
                 second = int(tmp[1]) 
                 data = next_setting - timedelta(seconds=second)
                 time_sched_on = data.strftime("%H:%M:%S")
             else:
                 time_sched_on = next_setting.strftime("%H:%M:%S")
                 
           if time_sched_off != "" and "sunrise" in time_sched_off:
             if "+" in time_sched_off or "-" in time_sched_off:
               if "+" in time_sched_off:
                 tmp = time_sched_off.split("+")
                 second = int(tmp[1]) 
                 data = next_rising + timedelta(seconds=second)
                 time_sched_off = data.strftime("%H:%M:%S")
               else:
                 tmp = time_sched_off.split("-")
                 second = int(tmp[1]) 
                 data = next_rising - timedelta(seconds=second)
                 time_sched_off = data.strftime("%H:%M:%S")
             else:
                 time_sched_off = next_rising.strftime("%H:%M:%S")                 
                  
           if time_sched_off != "" and "sunset" in time_sched_off:
             if "+" in time_sched_off or "-" in time_sched_off:
               if "+" in time_sched_off:
                 tmp = time_sched_off.split("+")
                 second = int(tmp[1]) 
                 data = next_setting + timedelta(seconds=second)
                 time_sched_off = data.strftime("%H:%M:%S")
               else:
                 tmp = time_sched_off.split("-")
                 second = int(tmp[1]) 
                 data = next_setting - timedelta(seconds=second)
                 time_sched_off = data.strftime("%H:%M:%S")
             else:
                 time_sched_off = next_setting.strftime("%H:%M:%S")                     
           
           sched_today = {
             "id" : sche["id"],
             "domain" : sche["domain"],
             "ON" : time_sched_on,
             "OFF" : time_sched_off,
           }
           scheduled_today.append(sched_today)
#    print(scheduled_today)
    
level_var = logging.NOTSET
with open("/data/options.json") as json_file:
     config = json.load(json_file)
     if config["log_level"] == "info":
           level_var = logging.INFO
name = FOLDER + "logfile"
logging.basicConfig(level=level_var, filename=name, filemode="w+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
mes = "Start Daemon PID: " + str(os.getpid())
logging.info( mes )
    
load_scheduled()

SUPERVISOR_TOKEN = os.environ['SUPERVISOR_TOKEN']
#print(SUPERVISOR_TOKEN)

get_sun()

get_schedule_today()
while ( 1 == 1 ): 
   now = datetime.now()
   
   current_time = now.strftime("%H:%M:%S")
   
   # Reload  new day
   if current_time == "00:00:01":
      get_sun()
      get_schedule_today()
      
   for sche in scheduled_today:
          time_sched = sche["ON"]
          if time_sched != "" and time_sched == current_time:
            call_service(sche["domain"],sche["id"],'on')
                 
          time_sched = sche["OFF"]
          if time_sched != "" and time_sched == current_time:
            call_service(sche["domain"],sche["id"],'off')


                  
   #print("Current Time =", current_time, )
   time.sleep(1)
