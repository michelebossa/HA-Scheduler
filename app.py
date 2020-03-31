from flask import Flask, render_template, request, redirect, flash
import os
import requests 
import json
import psutil


app = Flask(__name__)
scheduled = []
elements = []
SUPERVISOR_TOKEN = ""
pid = 0
def get_deamon_pid():
    global pid
    for process in psutil.process_iter():
      if '/share/scheduler/daemon.py' in process.cmdline():
         pid = process.pid
def write_scheduled(setting):
   filename = "/share/scheduler/" + setting["id"] + ".json"
   with open(filename, 'w') as outfile:
        json.dump(setting, outfile)
        
@app.route('/')
def index():
    get_deamon_pid()
    return render_template('index.html', elements=elements, scheduled=scheduled, pid = pid )

@app.route('/add', methods=["GET", "POST"])
def add():     
    if request.method == "GET":
        elem     = {'id':'',
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
        return render_template('edit.html',elem=elem, elements=elements, pid = pid )
    else:
#        print(request)
        data = request.form["id"].split("-")
        id = data[0]
        friendly_name = data[1]
        data = id.split(".")
        domain = data[0]
        enable = 'false'
        if 'enable' in request.form:
          enable = 'true'
        setting   = {'id': id,
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
        #return redirect(request.url)
        return render_template('edit.html',elem=setting, elements=elements, pid = pid)
@app.route('/delete/<id>', methods=["POST"])
def delete(id):   
        if id != "":
            filename = "/share/scheduler/" + id + ".json"
            os.remove(filename)
            run_daemon()
            load_scheduled()       
            flash('Deleted')
        return render_template('edit.html',elem=setting, elements=elements, pid = pid)        
@app.route('/item/<id>', methods=["GET", "POST"])
def edit(id):     
    if request.method == "GET":
        elem = {}
        for el in scheduled:
          if el["id"] == id:
            elem = el
        return render_template('edit.html',elem=elem, elements=elements, pid = pid)
    else: 
        #print(request)
        data = request.form["id"].split("-")
        id = data[0]
        friendly_name = data[1]
        data = id.split(".")
        domain = data[0]
        enable = 'false'
        if 'enable' in request.form:
          enable = 'true'
        setting   = {'id': id,
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
        return render_template('edit.html',elem=setting, elements=elements, pid = pid)
        
@app.route('/reload',methods=['POST'])
def reload():
    run_daemon()
    load_scheduled()
    get_elements()  
    return json.dumps({'html':'<span>All good !!</span>'})
 
    
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
    list = os.listdir('/share/scheduler/')
    for file in list:
       if ".json" in file:
         filename = "/share/scheduler/" + file
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
      if '/share/scheduler/daemon.py' in process.cmdline():
         print("Daemon Kill" , process.pid)
         os.system("kill " + str(process.pid))      

    os.system("python3 /share/scheduler/daemon.py &")
    print("Daemon Start")

if __name__ == '__main__':
                        
    SUPERVISOR_TOKEN = os.environ['SUPERVISOR_TOKEN']
    run_daemon()
    #print(SUPERVISOR_TOKEN)
    load_scheduled()
    get_elements()          
    app.secret_key = '7d441f27d441f27567d441f2b6176a'    
    app.run(debug=True, host='0.0.0.0', port=8099)
    