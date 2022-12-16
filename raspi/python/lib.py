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
settings = {"schedule" : sched}
settings_path = "raspi/python/settings.json"

def main():
    
    print("now in main")
    init()
    print("Done initializing")
    add_new_task(Weekday.FRIDAY.value,"23:25",10)
    
    while True:
        
        print("checking for tasks that need running")
        schedule.run_pending()
        print("Current task done")
        time.sleep(60)
    
def init():
    """
    This method initilizes the device by loading settings from the settings.json
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
        schedule.every().tuesday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
        
    for task_index in range(len(sched[2])):
        
        task = sched[2][task_index]
        schedule.every().wednesday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
        
    for task_index in range(len(sched[3])):
        
        task = sched[3][task_index]
        schedule.every().thursday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
        
    for task_index in range(len(sched[4])):
        
        task = sched[4][task_index]
        schedule.every().friday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
        
    for task_index in range(len(sched[5])):
        
        task = sched[5][task_index]
        schedule.every().saturday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
        
    for task_index in range(len(sched[6])):
        
        task = sched[6][task_index]
        schedule.every().sunday.at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
    
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
    print(task.toJSON())
    
    if weekday > 6:
        print(sched)
        for i in range(len(sched)):
            
            weekday_tasks = sched[i]
            was_added = False
            print(weekday_tasks)
    
            for saved_task in weekday_tasks:
        
                if same_task(saved_task, task):
            
                    saved_task.dispense_seconds = task.dispense_seconds
                    was_added = True
                    break
    
            if not was_added:
        
                weekday_tasks.append(task)
        
        print(sched)
    else:
        weekday_tasks = sched[weekday]
        was_added = False
    
        for saved_task in weekday_tasks:
        
            if same_task(saved_task, task):
            
                saved_task.dispense_seconds = task.dispense_seconds
                was_added = True
                break
    
        if not was_added:
        
            weekday_tasks.append(task)
        
    set_settings()
    put_new_task_on_schedule(weekday, task)

def get_settings():
    """
    This method gets the settings from settings.json 
    """
    global settings
    
    if os.path.exists(settings_path):
        
        json_settings = open(settings_path, "r")
        
        if (os.path.getsize(settings_path) <= 0):
            
            return
        
        settings = objectify_settings(json.load(json_settings))
        json_settings.close()   
    
    else:
        
        json_settings = open(settings_path, "x")
        json_settings.close()

def objectify_settings(settings_json):
    
    global settings
    settings ={}
    settings["schedule"] = objectify_schedule(settings_json.get("schedule"))
    return settings

def objectify_schedule(schedule_json):
    
    global sched
    sched = []
    
    for day_json in json.loads(schedule_json):

        day = []
        
        for task in day_json:
            
            day.append(Task(task.get("time"), task.get("dispense_seconds")))
            
        sched.append(day)
        
    return sched
    
def stringify_settings():
    
    stringified_settings = {}
    
    stringified_settings["schedule"] = stringify_schedule()
    
    return stringified_settings
    
def stringify_schedule():
    
    stringified_schedule = []
    
    for day in sched:
        
        stringified_day = []
        
        for task in day:
            
            stringified_day.append(task.toJSON())
            
        stringified_schedule.append(stringified_day)
        
    return json.dumps(stringified_schedule)

def set_settings():
    """
    This method sets the settings in settings.json.
    If the file doesn't exist it creates it.
    If the file exists it parses the settings, replaces unmatching ones and adds in non existent ones.
    """
    global settings
    
    if os.path.exists(settings_path):
        
        settings_file = open(settings_path,"r")
        settings_file_string = settings_file.read()
        settings_file.close()
        
    else:
        
        _ = open(settings_path,"x")
        _.close()
        settings_file_string = ""
    
    if(settings_file_string == ""):
        
        settings_file = open(settings_path,"w")
        json.dump(stringify_settings(), settings_file)
        settings_file.close()
        return

    settings_json = json.loads(settings_file_string)
    settings_json.update(stringify_settings())
    settings_file = open(settings_path,"w")
    json.dump(settings_json, settings_file)
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