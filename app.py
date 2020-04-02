from flask import Flask, render_template, request, redirect, flash
import os
import requests 
import json
import psutil
import random, string

app = Flask(__name__)
scheduled = []
elements = []
SUPERVISOR_TOKEN = ""
pid = 0
element_global = {}
sun = {}
FOLDER = "/share/ha-scheduler/"
def randomid(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))
   
def get_deamon_pid():
    global pid
    for process in psutil.process_iter():
      if '/home/daemon.py' in process.cmdline():
         pid = process.pid
def write_scheduled(setting):
   filename = FOLDER + setting["id"] + ".json"
   with open(filename, 'w') as outfile:
        json.dump(setting, outfile)
def get_sun():
   global sun 
   name = FOLDER + "sun.sun"
   try:
       with open(name) as json_file:
            sun = json.load(json_file)
   except IOError:
       print("File Sun")
@app.route('/')
def index():
    get_deamon_pid()
    get_sun()
    return render_template('index.html', elements=elements, scheduled=scheduled, pid = pid, sun=sun )

@app.route('/add', methods=["GET", "POST"])
def add():     
    if request.method == "GET":
        elem     = {'id':'',
                    'entity_id': '',
                    'friendly_name': '',
                    'domain': '',
                    'enable': 'true',
                    'ON_1': '',
                    'ON_2': '',
                    'ON_3': '',
                    'ON_4': '',
                    'ON_5': '',
                    'ON_6': '',
                    'ON_7': '',            
                    'OFF_1': '',
                    'OFF_2': '',
                    'OFF_3': '',
                    'OFF_4': '',
                    'OFF_5': '',
                    'OFF_6': '',
                    'OFF_7': ''            
                   }
        return render_template('edit.html',elem=elem, elements=elements, pid = pid, sun=sun )
    else:
#        print(request)
        if request.form["entity_id"] == "" or request.form["entity_id"] ==  "Select Entity":
            id = request.form["entity_id"]
            entity_id = ""
            friendly_name = ""
            domain = ""
        else:
            data = request.form["entity_id"].split("-")
            entity_id = data[0]
            friendly_name = data[1]
            data = entity_id.split(".")
            domain = data[0]
            id = randomid(20)
        
        enable = 'false'        
        if 'enable' in request.form:
          enable = 'true'
        setting   = {'id': id,
                    'entity_id': entity_id,
                    'friendly_name': friendly_name,
                    'domain': domain,
                    'enable': enable,
                    'ON_1': request.form["ON_1"],
                    'ON_2': request.form["ON_2"],
                    'ON_3': request.form["ON_3"],
                    'ON_4': request.form["ON_4"],
                    'ON_5': request.form["ON_5"],
                    'ON_6': request.form["ON_6"],
                    'ON_7': request.form["ON_7"],            
                    'OFF_1': request.form["OFF_1"],
                    'OFF_2': request.form["OFF_2"],
                    'OFF_3': request.form["OFF_3"],
                    'OFF_4': request.form["OFF_4"],
                    'OFF_5': request.form["OFF_5"],
                    'OFF_6': request.form["OFF_6"],
                    'OFF_7': request.form["OFF_7"],           
                   }    
        if id == "" or id ==  "Select Entity":
            flash('Error please fill entity id')
        else:
            write_scheduled(setting)   
            run_daemon()
            load_scheduled()       
            flash('Saved')
        #return redirect(request.url)
        return render_template('edit.html',elem=setting, elements=elements, pid = pid, sun=sun)
@app.route('/item/delete/<id>', methods=["GET", "POST"])
def delete(id):
        global element_global   
        if id != "":
            filename = FOLDER + id + ".json"
            os.remove(filename)
            run_daemon()
            load_scheduled()       
            flash('Deleted')
        return render_template('edit.html',elem=element_global, elements=elements, pid = pid, sun=sun)        
@app.route('/item/<id>', methods=["GET", "POST"])
def edit(id):     
    global element_global
    if request.method == "GET":
        elem = {}
        for el in scheduled:
          if el["id"] == id:
            elem = el
        
        element_global = elem       
        return render_template('edit.html',elem=elem, elements=elements, pid = pid, sun=sun)
    else: 
        #print(request)
        data = request.form["entity_id"].split("-")
        entity_id = data[0]
        friendly_name = data[1]
        data = entity_id.split(".")        
        domain = data[0]
        enable = 'false'
        if 'enable' in request.form:
          enable = 'true'
        setting   = {'id': id,
                     'entity_id': entity_id,
                    'friendly_name': friendly_name,
                    'domain': domain,
                    'enable': enable,
                    'ON_1': request.form["ON_1"],
                    'ON_2': request.form["ON_2"],
                    'ON_3': request.form["ON_3"],
                    'ON_4': request.form["ON_4"],
                    'ON_5': request.form["ON_5"],
                    'ON_6': request.form["ON_6"],
                    'ON_7': request.form["ON_7"],            
                    'OFF_1': request.form["OFF_1"],
                    'OFF_2': request.form["OFF_2"],
                    'OFF_3': request.form["OFF_3"],
                    'OFF_4': request.form["OFF_4"],
                    'OFF_5': request.form["OFF_5"],
                    'OFF_6': request.form["OFF_6"],
                    'OFF_7': request.form["OFF_7"],           
                   }    
        write_scheduled(setting)          
        run_daemon()
        load_scheduled()
        flash('Saved')
        element_global = setting 
        return render_template('edit.html',elem=setting, elements=elements, pid = pid, sun=sun)
        
@app.route('/reload',methods=['POST'])
def reload():
    run_daemon()
    load_scheduled()
    get_elements()  
    return json.dumps({'html':'<span>All good !!</span>'})
 
@app.route('/log',methods=['GET'])
def log():
   name = FOLDER + "logfile"
   data = ""
   try:
       with open(name) as file:
            data = file.read()
   except IOError:
       print("Missing Log")
   return render_template('log.html',data=data, pid = pid, sun=sun)
    
def get_elements():
    global elements    
    elements = []
    domains = ["automation","light","binary_sensor","switch","script"]
    URL = "http://hassio/homeassistant/api/states"
               
    # defining a params dict for the parameters to be sent to the API 
    Auth = 'Bearer ' + SUPERVISOR_TOKEN
    headers = {'content-type': 'application/json', 'Authorization' : Auth } 
          
    # sending get request and saving the response as response object 
    response = requests.get(url = URL, headers=headers) 
    json_data = response.json()



    for obj in json_data:
      element = {
        'id' : obj["entity_id"],
        'state' : obj["state"],
        'friendly_name' : "",
        'domain' : ""
      }

      
      attributes = obj["attributes"]
      if "friendly_name" in attributes:
        element["friendly_name"] = attributes["friendly_name"]
      data = element["id"].split(".")
      element["domain"] = data[0]
      if element["domain"] in domains:
         elements.append(element)
      elements = sorted(elements,key=lambda x:x['id'],reverse=False)
         
def load_scheduled():
    global scheduled
    scheduled = []
    list = os.listdir(FOLDER)
    for file in list:
       if ".json" in file:
         filename = FOLDER + file
         with open(filename) as json_file:
           data = json.load(json_file)
           scheduled.append(data)
           
    scheduled = sorted(scheduled,key=lambda x:x['id'],reverse=False)     
def call_service(dominio,id,action):
    URL = "http://hassio/homeassistant/api/services/" + dominio + "/turn_" + action
               
    # defining a params dict for the parameters to be sent to the API 
    Auth = 'Bearer ' + SUPERVISOR_TOKEN
    data = {'entity_id': 'switch.lume_relay'}
    print(Auth)
    headers = {'content-type': 'application/json', 'Authorization' : Auth } 
          
    # sending get request and saving the response as response object 
    response = requests.post(url = URL, headers=headers,json=data) 
    print(id, " Turn " , action)

def run_daemon():
    for process in psutil.process_iter():
      if '/home/daemon.py' in process.cmdline():
         print("Daemon Kill" , process.pid)
         os.system("kill " + str(process.pid))      

    os.system("python3 /home/daemon.py &")
    print("Daemon Start")

if __name__ == '__main__':
                        
    SUPERVISOR_TOKEN = os.environ['SUPERVISOR_TOKEN']
    run_daemon()
    #print(SUPERVISOR_TOKEN)
    load_scheduled()
    get_elements()      
    get_sun()    
    app.secret_key = '7d441f27d441f27567d441f2b6176a'    
    app.run(debug=True, host='0.0.0.0', port=8099)
    