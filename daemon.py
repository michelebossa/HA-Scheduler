import requests 
from datetime import datetime, timezone, timedelta
import time
import json
import os
import logging
import threading

scheduled = []
scheduled_today = []
next_setting = ""
next_rising = ""
day_sun = ""
FOLDER = "/share/ha-scheduler/"
config = {}
max_retries = 2
max_retry_interval = 5 
def load_scheduled():
    active = 0
    disabled = 0
    list = os.listdir(FOLDER)
    for file in list:
       if ".json" in file:
         filename = FOLDER + file
         with open(filename) as json_file:
           sche = json.load(json_file)
           if sche["enable"] == "true":
              active += 1
              scheduled.append(sche)
           else:
              disabled += 1
    mes = "Active " + str(active) + " Disabled " + str(disabled)
    logging.info( mes )

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
    global day_sun
    next_setting = datetime.strptime(json_data["next_setting"], '%Y-%m-%dT%H:%M:%S%z')     
    next_setting = next_setting.replace(tzinfo=timezone.utc).astimezone(tz=None)    
    next_rising = datetime.strptime(json_data["next_rising"], '%Y-%m-%dT%H:%M:%S%z')      
    next_rising = next_rising.replace(tzinfo=timezone.utc).astimezone(tz=None)
    found = "false"
    if day_sun == "":
      day_sun = datetime.now().strftime("%d")
      found = "true"
    elif next_rising.strftime("%d") == next_setting.strftime("%d") and next_rising.strftime("%d") == datetime.now().strftime("%d"):  
      day_sun = datetime.now().strftime("%d")
      found = "true"
    # else:
      # day_sun == ""
            
    if found == "true":
       filename = FOLDER + "sun.sun"
       sun = { 
             "day"     : day_sun,
             "sunrise" : next_rising.strftime("%H:%M:%S"),
             "sunset" : next_setting.strftime("%H:%M:%S")
        }
       with open(filename, 'w') as outfile:
            json.dump(sun, outfile)
            
        #print("Sunset", next_setting.strftime("%H:%M:%S") , "Sunrise", next_rising.strftime("%H:%M:%S") )
       mes = "Sunrise " + next_rising.strftime("%H:%M:%S") + " Sunset " + next_setting.strftime("%H:%M:%S") 
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
    mes = str(id) + " Turn " + str(action) + " " + str(response.status_code) 
    logging.info( mes )
    time.sleep(0.5)

def get_second(input):
   if "S" in input:
     return  int(input.split("S")[0])
   elif "M" in input:
     seconds = input.split("M")[0] 
     seconds = int(seconds)*60
     return int(seconds)
   else: 
     return int(input)
     
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
                 second = get_second(tmp[1]) 
                 data = next_rising + timedelta(seconds=second)
                 time_sched_on = data.strftime("%H:%M:%S")
               else:
                 tmp = time_sched_on.split("-")
                 second = get_second(tmp[1]) 
                 data = next_rising - timedelta(seconds=second)                 
                 time_sched_on = data.strftime("%H:%M:%S")
             else:
                 time_sched_on = next_rising.strftime("%H:%M:%S")
                 
           if time_sched_on != "" and "sunset" in time_sched_on:
             if "+" in time_sched_on or "-" in time_sched_on:
               if "+" in time_sched_on:
                 tmp = time_sched_on.split("+")
                 second = get_second(tmp[1]) 
                 data = next_setting + timedelta(seconds=second)
                 time_sched_on = data.strftime("%H:%M:%S")
               else:
                 tmp = time_sched_on.split("-")
                 second = get_second(tmp[1]) 
                 data = next_setting - timedelta(seconds=second)
                 time_sched_on = data.strftime("%H:%M:%S")
             else:
                 time_sched_on = next_setting.strftime("%H:%M:%S")
                 
           if time_sched_off != "" and "sunrise" in time_sched_off:
             if "+" in time_sched_off or "-" in time_sched_off:
               if "+" in time_sched_off:
                 tmp = time_sched_off.split("+")
                 second = get_second(tmp[1]) 
                 data = next_rising + timedelta(seconds=second)
                 time_sched_off = data.strftime("%H:%M:%S")
               else:
                 tmp = time_sched_off.split("-")
                 second = get_second(tmp[1]) 
                 data = next_rising - timedelta(seconds=second)
                 time_sched_off = data.strftime("%H:%M:%S")
             else:
                 time_sched_off = next_rising.strftime("%H:%M:%S")                 
                  
           if time_sched_off != "" and "sunset" in time_sched_off:
             if "+" in time_sched_off or "-" in time_sched_off:
               if "+" in time_sched_off:
                 tmp = time_sched_off.split("+")
                 second = get_second(tmp[1]) 
                 data = next_setting + timedelta(seconds=second)
                 time_sched_off = data.strftime("%H:%M:%S")
               else:
                 tmp = time_sched_off.split("-")
                 second = get_second(tmp[1]) 
                 data = next_setting - timedelta(seconds=second)
                 time_sched_off = data.strftime("%H:%M:%S")
             else:
                 time_sched_off = next_setting.strftime("%H:%M:%S")                     
           
           sched_today = {
             "id" : sche["id"],
             "entity_id": sche["entity_id"],
             "domain" : sche["domain"],
             "ON" : time_sched_on,
             "OFF" : time_sched_off,
           }
           scheduled_today.append(sched_today)
    for sched in scheduled_today:
       mes = sched["entity_id"] + " ON "+ sched["ON"]  + " OFF "+ sched["OFF"]
       logging.info( mes )
    
level_var = logging.NOTSET
with open("/data/options.json") as json_file:
     config = json.load(json_file)
     if config["log_level"] == "info":
           level_var = logging.INFO
     if "max_retries" in config:
        max_retries = config["max_retries"]
     if "max_retry_interval" in config:
        max_retries = config["max_retry_interval"]  
        
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

threadLock = threading.Lock()
class call_HA (threading.Thread):
   def __init__(self, dominio, id, azione):
      threading.Thread.__init__(self)
      self.dominio = dominio
      self.id = id
      self.azione = azione
   def run(self):
      # Acquisizione del lock
      threadLock.acquire()
      call_service(self.dominio,self.id,self.azione)
      # Rilascio del lock
      threadLock.release()
      

class check_HA (threading.Thread):
   def __init__(self, elements):
      threading.Thread.__init__(self)
      self.elements = elements
   def run(self):
      # Acquisizione del lock
      threadLock.acquire()
      time.sleep(max_retry_interval)
      URL = "http://hassio/homeassistant/api/states"
                   
      # defining a params dict for the parameters to be sent to the API 
      Auth = 'Bearer ' + SUPERVISOR_TOKEN
      # print(Auth)
      headers = {'content-type': 'application/json', 'Authorization' : Auth } 
              
      # sending get request and saving the response as response object 
      response = requests.get(url = URL, headers=headers) 
      json_data = response.json()   
       
      for obj in json_data:        
          for elem in self.elements:
              if obj["entity_id"] ==  elem["id"]:
                if obj["state"] != elem["state"]:
                   call_service(elem["domain"],elem["id"],elem["state"])
      # Rilascio del lock
      threadLock.release()
elements_check = []         
while ( 1 == 1 ): 
   now = datetime.now()
   
   current_time = now.strftime("%H:%M:%S")
   day = now.strftime("%d")
   # Reload  new day
   if day_sun != day: #current_time == "00:00:01":
       get_sun()
       if day_sun == day:
          get_schedule_today()

   for sche in scheduled_today:
          time_sched = sche["ON"]
          if time_sched != "" and time_sched == current_time:
            # call_service(sche["domain"],sche["entity_id"],'on')
            thread1 = call_HA(sche["domain"],sche["entity_id"],'on')
            thread1.start()
            element = {
              'id' : sche["entity_id"],
              'state' : "on",
              'domain' : sche["domain"]
              }
            elements_check.append(element) 
                 
          time_sched = sche["OFF"]
          if time_sched != "" and time_sched == current_time:
            # call_service(sche["domain"],sche["entity_id"],'off')
            thread1 = call_HA(sche["domain"],sche["entity_id"],'off')
            thread1.start()
            element = {
              'id' : sche["entity_id"],
              'state' : "off",
              'domain' : sche["domain"]
              }
            elements_check.append(element) 
   if not elements_check:
      elements_check = []  
   else:   
      times = max_retries
      while times > 0:
        thread1 = check_HA(elements_check)
        thread1.start()                
        times -= 1  
      elements_check = []
   #print("Current Time =", current_time, )
   time.sleep(1)
