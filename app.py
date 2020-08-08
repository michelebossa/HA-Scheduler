from flask import Flask, render_template, request, redirect, flash
import os
import requests
import json
import psutil
import logging
import random
import string

app = Flask(__name__)
scheduled = []
elements = []
SUPERVISOR_TOKEN = ""
pid = 0
element_global = {}
sun = {}
FOLDER = "/share/ha-scheduler/"
bk_color = "#f8f9fa"


def randomid(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def get_deamon_pid():
    global pid
    for process in psutil.process_iter():
        if "/home/daemon.py" in process.cmdline():
            pid = process.pid


def write_scheduled(setting):
    filename = FOLDER + setting["id"] + ".json"
    with open(filename, "w") as outfile:
        json.dump(setting, outfile)


def get_sun():
    global sun
    name = FOLDER + "sun.sun"
    try:
        with open(name) as json_file:
            sun = json.load(json_file)
    except IOError:
        print("File Sun")


@app.route("/")
def index():
    get_deamon_pid()
    get_sun()
    return render_template(
        "index.html",
        elements=elements,
        scheduled=scheduled,
        pid=pid,
        sun=sun,
        bk_color=bk_color,
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    try:
        global element_global
        if request.method == "GET":
            entity_id = []
            entity = {"entity_id": "", "domain": "", "friendly_name": ""}
            entity_id.append(entity)
            elem = {
                "id": "",
                "entity_id": entity_id,
                "friendly_name": "",
                "enable": "true",
                "enable_1": "true",
                "enable_2": "true",
                "enable_3": "true",
                "enable_4": "true",
                "enable_5": "true",
                "enable_6": "true",
                "enable_7": "true",
                "ON_1": "",
                "ON_2": "",
                "ON_3": "",
                "ON_4": "",
                "ON_5": "",
                "ON_6": "",
                "ON_7": "",
                "OFF_1": "",
                "OFF_2": "",
                "OFF_3": "",
                "OFF_4": "",
                "OFF_5": "",
                "OFF_6": "",
                "OFF_7": "",
            }
            element_global = elem
            return render_template(
                "edit.html",
                elem=elem,
                elements=elements,
                pid=pid,
                sun=sun,
                bk_color=bk_color,
            )
        else:
            entity_id = []
            i = 0
            while True:
                i += 1
                name = "entity_id_" + str(i)
                if name in request.form:
                    if (
                        request.form[name] != "Select Entity"
                        and request.form[name] != ""
                    ):
                        data = request.form[name].split(".")
                        domain = data[0]
                        data = request.form[name].split("-")
                        friendly_name = data[1]
                        entity = {
                            "entity_id": data[0],
                            "domain": domain,
                            "friendly_name": friendly_name,
                        }
                        entity_id.append(entity)
                        print(entity)
                else:
                    break
            print(entity_id)

            friendly_name = request.form["friendly_name"]
            id = randomid(20)
            enable = "false"
            enable_1 = "false"
            enable_2 = "false"
            enable_3 = "false"
            enable_4 = "false"
            enable_5 = "false"
            enable_6 = "false"
            enable_7 = "false"
            if "enable" in request.form:
                enable = "true"
            if "enable_1" in request.form:
                enable_1 = "true"
            if "enable_2" in request.form:
                enable_2 = "true"
            if "enable_3" in request.form:
                enable_3 = "true"
            if "enable_4" in request.form:
                enable_4 = "true"
            if "enable_5" in request.form:
                enable_5 = "true"
            if "enable_6" in request.form:
                enable_6 = "true"
            if "enable_7" in request.form:
                enable_7 = "true"

            setting = {
                "id": id,
                "entity_id": entity_id,
                "friendly_name": friendly_name,
                "enable": enable,
                "enable_1": enable_1,
                "enable_2": enable_2,
                "enable_3": enable_3,
                "enable_4": enable_4,
                "enable_5": enable_5,
                "enable_6": enable_6,
                "enable_7": enable_7,
                "ON_1": request.form["ON_1"],
                "ON_2": request.form["ON_2"],
                "ON_3": request.form["ON_3"],
                "ON_4": request.form["ON_4"],
                "ON_5": request.form["ON_5"],
                "ON_6": request.form["ON_6"],
                "ON_7": request.form["ON_7"],
                "OFF_1": request.form["OFF_1"],
                "OFF_2": request.form["OFF_2"],
                "OFF_3": request.form["OFF_3"],
                "OFF_4": request.form["OFF_4"],
                "OFF_5": request.form["OFF_5"],
                "OFF_6": request.form["OFF_6"],
                "OFF_7": request.form["OFF_7"],
            }
            if entity_id == []:
                flash("Error please fill entity id")
                entity_id = []
                entity = {"entity_id": "", "domain": "", "friendly_name": ""}
                setting["entity_id"].append(entity)
            else:
                write_scheduled(setting)
                run_daemon()
                load_scheduled()
                flash("Saved")
            element_global = setting
            return render_template(
                "edit.html",
                elem=setting,
                elements=elements,
                pid=pid,
                sun=sun,
                bk_color=bk_color,
            )
    except Exception as e:
        return e.__repr__()


@app.route("/item/add_elem", methods=["GET", "POST"])
def add_elem():
    global element_global
    entity = {"entity_id": "", "domain": "", "friendly_name": ""}
    element_global["entity_id"].append(entity)
    return render_template(
        "edit.html",
        elem=element_global,
        elements=elements,
        pid=pid,
        sun=sun,
        bk_color=bk_color,
    )


@app.route("/item/remove_elem/<index>", methods=["GET", "POST"])
def remove_elem(index):
    global element_global
    indx = int(index)
    indx = indx - 1
    del element_global["entity_id"][indx]
    return render_template(
        "edit.html",
        elem=element_global,
        elements=elements,
        pid=pid,
        sun=sun,
        bk_color=bk_color,
    )


@app.route("/item/delete/<id>", methods=["GET", "POST"])
def delete(id):
    global element_global
    if id != "":
        filename = FOLDER + id + ".json"
        os.remove(filename)
        run_daemon()
        load_scheduled()
        flash("Deleted")
    return render_template(
        "edit.html",
        elem=element_global,
        elements=elements,
        pid=pid,
        sun=sun,
        bk_color=bk_color,
    )


@app.route("/item/<id>", methods=["GET", "POST"])
def edit(id):
    global element_global
    if request.method == "GET":
        elem = {}
        for el in scheduled:
            if el["id"] == id:
                elem = el

        element_global = elem
        return render_template(
            "edit.html",
            elem=elem,
            elements=elements,
            pid=pid,
            sun=sun,
            bk_color=bk_color,
        )
    else:
        i = 0
        entity_id = []
        while True:
            i += 1
            name = "entity_id_" + str(i)
            if name in request.form:
                if request.form[name] != "Select Entity" and request.form[name] != "":
                    data = request.form[name].split(".")
                    domain = data[0]
                    data = request.form[name].split("-")
                    friendly_name = data[1]
                    entity = {
                        "entity_id": data[0],
                        "domain": domain,
                        "friendly_name": friendly_name,
                    }
                    entity_id.append(entity)
            else:
                break
        friendly_name = request.form["friendly_name"]
        enable = "false"
        enable_1 = "false"
        enable_2 = "false"
        enable_3 = "false"
        enable_4 = "false"
        enable_5 = "false"
        enable_6 = "false"
        enable_7 = "false"
        if "enable" in request.form:
            enable = "true"
        if "enable_1" in request.form:
            enable_1 = "true"
        if "enable_2" in request.form:
            enable_2 = "true"
        if "enable_3" in request.form:
            enable_3 = "true"
        if "enable_4" in request.form:
            enable_4 = "true"
        if "enable_5" in request.form:
            enable_5 = "true"
        if "enable_6" in request.form:
            enable_6 = "true"
        if "enable_7" in request.form:
            enable_7 = "true"
        setting = {
            "id": id,
            "entity_id": entity_id,
            "friendly_name": friendly_name,
            "domain": domain,
            "enable": enable,
            "enable_1": enable_1,
            "enable_2": enable_2,
            "enable_3": enable_3,
            "enable_4": enable_4,
            "enable_5": enable_5,
            "enable_6": enable_6,
            "enable_7": enable_7,
            "ON_1": request.form["ON_1"],
            "ON_2": request.form["ON_2"],
            "ON_3": request.form["ON_3"],
            "ON_4": request.form["ON_4"],
            "ON_5": request.form["ON_5"],
            "ON_6": request.form["ON_6"],
            "ON_7": request.form["ON_7"],
            "OFF_1": request.form["OFF_1"],
            "OFF_2": request.form["OFF_2"],
            "OFF_3": request.form["OFF_3"],
            "OFF_4": request.form["OFF_4"],
            "OFF_5": request.form["OFF_5"],
            "OFF_6": request.form["OFF_6"],
            "OFF_7": request.form["OFF_7"],
        }
        write_scheduled(setting)
        run_daemon()
        load_scheduled()
        flash("Saved")
        element_global = setting
        return render_template(
            "edit.html",
            elem=setting,
            elements=elements,
            pid=pid,
            sun=sun,
            bk_color=bk_color,
        )


@app.route("/reload", methods=["POST"])
def reload():
    run_daemon()
    load_scheduled()
    get_elements()
    return json.dumps({"html": "<span>All good !!</span>"})


@app.route("/log", methods=["GET"])
def log():
    name = FOLDER + "logfile"
    data = ""
    try:
        with open(name) as file:
            data = file.read()
    except IOError:
        print("Missing Log")
    return render_template("log.html", data=data, pid=pid, sun=sun, bk_color=bk_color)


def get_elements():
    global elements
    elements = []
    domains = [
        "automation",
        "light",
        "binary_sensor",
        "switch",
        "script",
        "climate",
        "cover",
        "input_boolean",
        "fan",
    ]
    URL = "http://hassio/homeassistant/api/states"

    # defining a params dict for the parameters to be sent to the API
    Auth = "Bearer " + SUPERVISOR_TOKEN
    headers = {"content-type": "application/json", "Authorization": Auth}

    # sending get request and saving the response as response object
    response = requests.get(url=URL, headers=headers)
    json_data = response.json()

    for obj in json_data:
        element = {
            "id": obj["entity_id"],
            "state": obj["state"],
            "friendly_name": "",
            "domain": "",
        }

        attributes = obj["attributes"]
        if "friendly_name" in attributes:
            element["friendly_name"] = attributes["friendly_name"]
        data = element["id"].split(".")
        element["domain"] = data[0]
        if element["domain"] in domains:
            elements.append(element)
        elements = sorted(elements, key=lambda x: x["id"], reverse=False)


def load_scheduled():
    global scheduled
    scheduled = []
    listf = os.listdir(FOLDER)
    for file in listf:
        if ".json" in file:
            filename = FOLDER + file
            with open(filename) as json_file:
                data = json.load(json_file)
                if not "enable_1" in data:
                    data["enable_1"] = "true"
                if not "enable_2" in data:
                    data["enable_2"] = "true"
                if not "enable_3" in data:
                    data["enable_3"] = "true"
                if not "enable_4" in data:
                    data["enable_4"] = "true"
                if not "enable_5" in data:
                    data["enable_5"] = "true"
                if not "enable_6" in data:
                    data["enable_6"] = "true"
                if not "enable_7" in data:
                    data["enable_7"] = "true"
                ele = data["entity_id"]
                if not isinstance(ele, list):
                    entity_id = []
                    tmp = ele.split(".")
                    domain = tmp[0]
                    entity = {
                        "entity_id": tmp[0],
                        "domain": domain,
                        "friendly_name": data["friendly_name"],
                    }
                    entity_id.append(entity)
                    data["entity_id"] = entity_id

                scheduled.append(data)

    scheduled = sorted(scheduled, key=lambda x: x["friendly_name"], reverse=False)


def run_daemon():
    for process in psutil.process_iter():
        if "/home/daemon.py" in process.cmdline():
            print("Daemon Kill", process.pid)
            os.system("kill " + str(process.pid))

    os.system("python3 /home/daemon.py &")
    print("Daemon Start")


if __name__ == "__main__":

    SUPERVISOR_TOKEN = os.environ["SUPERVISOR_TOKEN"]
    with open("/data/options.json") as json_file:
        config = json.load(json_file)
        if "bk_color" in config:
            if config["bk_color"] != "":
                bk_color = config["bk_color"]

    run_daemon()
    load_scheduled()
    get_elements()
    get_sun()
    app.secret_key = "7d441f27d441f27567d441f2b6176a"
    app.run(debug=False, host="0.0.0.0", port=8099)
