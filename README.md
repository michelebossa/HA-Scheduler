# HA-Scheduler
Scheduler Addon Home Hassistant

This addon give us the possibility to handle a simple week configuration of automation, light,binary_sensor, switch and script.


![main](https://raw.githubusercontent.com/michelebossa/HA-Scheduler/master/main.png)


Entity setting section:

We can set on or off action every day with follow format:


No action on this day					No Fill	
Time format 							HH:MM:SS
Action at sunrise/ sunset 				sunrise/sunset
Offset + or - at sunrise or sunset      sunrise+30M   (M = Minutes, S = Second)

![edit](https://raw.githubusercontent.com/michelebossa/HA-Scheduler/master/edit.png)


# Installation

Copy the url of this addon into "Supervisor" -> "Addon Store" -> "Add New repository URL" after install it.

# Configuration

    log_level: Level of logging messages default info 
	max_retries: Number of retrying action default 2
	max_retry_interval: How many seconds to wait before retrying. default 5
	
	
	