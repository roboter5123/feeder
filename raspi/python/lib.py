from gpiozero import Motor
from Weekday import Weekday
import json
import time
import schedule
from Task import Task
import os

motor_forward_pin = 18
motor_backward_pin = 17
motor = Motor(motor_forward_pin, motor_backward_pin)
empty_schedule = [[],[],[],[],[],[],[]]
settings = {}
sched = {}

def init():
    """
    This method initilizes the device by loading settings from th settings.json
    """
    
    global settings
    global sched
    settings = get_settings()
    
    if settings == {}:
        
        settings["schedule"] = empty_schedule
        
    sched = settings.get("schedule")

def add_new_task(weekday: int, time : str, dispense_seconds: int):
    
    global settings
    global sched
    
    task = Task(time, dispense_seconds)
    weekday_tasks = sched[weekday]
    was_added = False
    
    for saved_task in weekday_tasks:
        
        if same_task(saved_task, task):
            
            saved_task.dispense_seconds = task.dispense_seconds
            was_added = True
            break
    
    if not was_added:
        
        weekday_tasks.append(task)
        
    sched[weekday] = weekday_tasks
    settings["schedule"] = sched
    set_settings(settings)

def get_settings() -> dict:
    """
    This method gets the settings from feeder/raspi/python/settings.json 
    and returns them as a dict.
    """
    global settings
    
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
    
    if os.path.exists("settings.json"):
        
        settings_file = open("settings.json","r")
        settings_file_string = settings_file.read()
        settings_file.close()
        
    else:
        
        _ = open("settings.json","x")
        _.close()
        settings_file_string = ""
    
    if(settings_file_string == ""):
        
        settings_file = open("settings.json","w")
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
    print(f"turning for {dispense_seconds} seconds")
    time.sleep(dispense_seconds)
    motor.stop()
    print("Stopped turning")
    return 

def same_task(task1: Task, task2: Task) -> bool:
    
    return task1.time == task2.time

init()
add_new_task(Weekday.MONDAY.value, "12:00",10)