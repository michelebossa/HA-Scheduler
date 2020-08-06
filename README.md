# HA-Scheduler
Scheduler Addon Home Hassistant

This addon give us the possibility to handle a simple week configuration of automation, light, binary_sensor, climate, cover, switch and script.


![main](https://raw.githubusercontent.com/michelebossa/HA-Scheduler/master/main.png)


Entity setting section:

We can made a group and set on or off action every day with follow format:


- No Fill									( No action on this day	)					
- HH:MM:SS									( Time format ) 							
- sunrise/sunset							( Action at sunrise/ sunset 				sunrise/sunset )
- sunrise+30M   (M = Minutes, S = Second)	( Offset + or - at sunrise or sunset )  
- :T27										(:T + temperature to set)  
- :B50										(:B + brightness value between 0 <> 100 to set) only light entity BETA   

![edit](https://raw.githubusercontent.com/michelebossa/HA-Scheduler/master/edit.png)


# Installation

Copy the url of this addon into "Supervisor" -> "Addon Store" -> "Add New repository URL" after install it.

# Configuration

    log_level: Level of logging messages default info 
	max_retries: Number of retrying action default 2
	max_retry_interval: How many seconds to wait before retrying. default 5
	bk_color: The background color default vaule #f8f9fa (white) 

## Home Assistant service
There is the possibility to enable or disable an entity by call these service on you automation/script:

```yaml
service: hassio.addon_stdin
data:
  addon: 998c1fd8_homeassistantscheduler
  input: light_group:enable_on
```

	addon = name of addon 
	input = group name:action (enable_on or enable_off)

<a target="_blank" href="https://www.buymeacoffee.com/michelebossa" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>