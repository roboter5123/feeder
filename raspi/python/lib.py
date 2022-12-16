from gpiozero import Motor
from Weekday import Weekday
import json
import time
from Task import Task
import os
import copy
import schedule

motor_forward_pin = 18
motor_backward_pin = 17
motor = Motor(motor_forward_pin, motor_backward_pin)
sched = [[],[],[],[],[],[],[]]
settings = {sched}


def main():
    
    print("now in main")
    add_new_task(Weekday.FRIDAY.value, "23:25",10)
    init()
    print("Done initializing")
    
    while True:
        
        print("checking for tasks that need running")
        schedule.run_pending()
        print("Current task done")
        time.sleep(60)
    
def init():
    """
    This method initilizes the device by loading settings from th settings.json
    """
    get_settings()
    init_schedule() 
    pass

def init_schedule():
    
    for task_index in range(len(sched[0])):
        
        task = sched[0][task_index]
        schedule.every().monday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
        
    for task_index in range(len(sched[1])):
        
        task = sched[1][task_index]
        schedule.every().tuesday.at(task.time).do(dispense(dispense,dispense_seconds = task.dispense_seconds))
        
    for task_index in range(len(sched[2])):
        
        task = sched[2][task_index]
        schedule.every().wednesday.at(task.time).do(dispense(dispense,dispense_seconds = task.dispense_seconds))
        
    for task_index in range(len(sched[3])):
        
        task = sched[3][task_index]
        schedule.every().thursday.at(task.time).do(dispense(dispense,dispense_seconds = task.dispense_seconds))
        
    for task_index in range(len(sched[4])):
        
        task = sched[4][task_index]
        schedule.every().friday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
        
    for task_index in range(len(sched[5])):
        
        task = sched[5][task_index]
        schedule.every().saturday.at(task.time).do(dispense(dispense,dispense_seconds = task.dispense_seconds))
        
    for task_index in range(len(sched[6])):
        
        task = sched[6][task_index]
        schedule.every().sunday.at(task.time).do(dispense(dispense,dispense_seconds = task.dispense_seconds))
    
def put_new_task_on_schedule(weekday: int, task: Task):
    
    if (weekday == 0):
        
        schedule.every().monday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
    
    elif(weekday == 1):
        
        schedule.every().tuesday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
        
    elif(weekday == 2):
        
        schedule.every().wednesday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)         
        
    elif(weekday == 3):
        
        schedule.every().thursday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)  
        
    elif(weekday == 4):
        
        schedule.every().friday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)  
        
    elif(weekday == 5):
        
        schedule.every().saturday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)  
        
    elif(weekday == 6):
        
        schedule.every().sunday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)  
        
    elif(weekday == 7):
        
        schedule.every().day.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
         
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
        
        
    put_new_task_on_schedule(weekday, task)

def get_settings() -> dict:
    """
    This method gets the settings from feeder/raspi/python/settings.json 
    and returns them as a dict.
    """
    global settings
    
    if os.path.exists("settings.json"):
        
        json_settings = open("settings.json", "r")
        settings = json.load(json_settings)
        json_settings.close()   
    
    else:
        
        json_settings = open("settings.json", "w")
        json.dump(settings,json_settings)
        json_settings.close()
        
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

