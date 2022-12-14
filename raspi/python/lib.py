from gpiozero import Motor
import Weekday
import json
import time
import schedule
import Task
import os

motor_forward_pin = 17
motor_backward_pin = 18
motor = Motor(motor_forward_pin, motor_backward_pin)
empty_schedule_dict = {Weekday.MONDAY:[],Weekday.TUESDAY:[],Weekday.WEDNESDAY:[],Weekday.THIRSDAY:[],Weekday.FRIDAY:[],Weekday.SATURDAY:[],Weekday.SUNDAY:[]}
settings = {}
sched = {}

def init():
    """
    This method initilizes the device by loading settings from th settings.json
    """
    
    settings = get_settings()
    
    if settings == {}:
        
        settings.update("schedule", empty_schedule_dict)
        
    sched = settings.get("schedule")

def add_new_task(weekday: Weekday, time : str, dispense_seconds: int):
    
    task = Task(time, dispense_seconds)
    weekday_tasks = sched.get(weekday)
    was_added = False
    
    for saved_task in weekday_tasks:
        
        if saved_task.same_task(task):
            
            saved_task.dispense_seconds = task.dispense_seconds
            was_added = True
            break
    
    if not was_added:
        
        weekday_tasks.append(task)

def get_settings() -> dict:
    """
    This method gets the settings from feeder/raspi/python/settings.json 
    and returns them as a dict.
    """
    
    if os.path.exists("feeder/raspi/python/settings.json"):
        
        json_settings = open("feeder/raspi/python/settings.json", "r")
        settings = json.load(json_settings)
        json_settings.close()
    
        return settings
    
    else:
        
        return {}

def set_settings(settings: dict) -> None:
    """
    This method sets the settings in feeder/raspi/python/settings.json.
    If the file doesn't exist it creates it.
    If the file exists it parses the settings, replaces unmatching ones and adds in non existent ones.
    """
    
    if os.path.exists("feeder/raspi/python/settings.json"):
        
        settings_file = open("feeder/raspi/python/settings.json","r")
        settings_file_string = settings_file.read()
        settings_file.close()
        
    else:
        
        _ = open("feeder/raspi/python/settings.json","x")
        _.close()
        settings_file_string = ""
    
    if(settings_file_string == ""):
        
        settings_file = open("feeder/raspi/python/settings.json","w")
        json.dump(settings, settings_file)
        settings_file.close()
        return

    json_settings = settings
    
    for setting in json.loads(settings_file_string):
        
        if not json_settings.get(setting, False) or json_settings.get(setting, False) != settings.get(setting):
            
            json_settings[setting] = settings[setting]
            
    settings_file = open("feeder/raspi/python/settings.json","w")
    json.dump(json_settings, settings_file)
    settings_file.close()
        
    return

def dispense(dispense_seconds: int) -> None:

    motor.forward()
    print(f"turning for {seconds} seconds")
    time.sleep(seconds)
    motor.stop()
    print("Stopped turning")
    return 

