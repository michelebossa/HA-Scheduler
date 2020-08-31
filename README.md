# HA-Scheduler
Scheduler Addon for Home Hassistant

This addon handles a week of configuration for:
- automation
- climate
- cover
- fan
- input_boolean
- light
- script
- switch
[![code style](https://img.shields.io/badge/Code%20style-Black-black)](https://black.now.sh/)

![main](https://raw.githubusercontent.com/michelebossa/HA-Scheduler/master/main.png)


Edit section:

We can make a group and set on or off action every day with following format:


- No Fill									( No action on this day	)					
- HH:MM:SS									( Time format ) 							
- sunrise/sunset							( Action at sunrise/ sunset 				sunrise/sunset )
- sunrise+30M   (M = Minutes, S = Second)	( Offset + or - at sunrise or sunset )  
- :T27										(:T + temperature to set)  
- :B50										(:B + brightness value between 0 <> 100 to set) only light entity BETA   

![edit](https://raw.githubusercontent.com/michelebossa/HA-Scheduler/master/edit.png)


# Installation

Copy the url of this addon into "Supervisor" -> "Addon Store" -> "Add New repository URL", and then close the dialog. Scroll down, choose "HA-Scheduler", and install it.

# Configuration

    log_level: Level of logging messages default info
	max_retries: Number of retrying action default 2
	max_retry_interval: How many seconds to wait before retrying. default 5
	bk_color: The background color default vaule #f8f9fa (white)

## Home Assistant service
There is the possibility to enable or disable an entity by calling this service on your automation/script:

```yaml
service: hassio.addon_stdin
data:
  addon: 998c1fd8_homeassistantscheduler
  input: light_group:enable_on
```

	addon = name of addon
	input = group name:action (enable_on or enable_off)

<a target="_blank" href="https://www.buymeacoffee.com/michelebossa" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>
