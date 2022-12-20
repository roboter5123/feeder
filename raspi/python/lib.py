from gpiozero import Motor
from Weekday import Weekday
import json
import time
from Task import Task
import os
import schedule
import threading
import datetime
import re
from uuid6 import uuid7

#Type aliases
Json_task = dict[str, any]
Json_day = list[Json_task]
Json_sched = dict[int,Json_day]

#Global variables
motor_forward_pin: int = 18
motor_backward_pin: int = 17
motor: Motor = Motor(motor_forward_pin, motor_backward_pin)
sched: dict[Weekday, list[Task]] = {Weekday.monday:[],Weekday.tuesday:[],Weekday.wednesday:[],Weekday.thursday:[],Weekday.friday:[],Weekday.saturday:[],Weekday.sunday:[]}
settings: dict[str,any] = {"schedule" : sched}
current_time :datetime = datetime.datetime.now()
settings_path: str = "raspi/python/settings.json"
logs_path: str = "raspi/python/logs/log-"

def main() -> None:
    """
    Main loop for the device.
    Initiates the device and then checks once every minute for tasks that need doing.
    """
    
    while True:
        
        task_thread = threading.Thread(target=execute_current_tasks, daemon=True)
        task_thread.start()
        time.sleep(60)
      
def init() -> None:
    """
    Initilizes the device by loading settings from the settings.json
    and settign up the schedule.
    """
    
    global current_time
    global logs_path
    
    logs_path += f"{current_time.year}-{current_time.month}-{current_time.day}-{current_time.hour}-{current_time.minute}-{current_time.second}.txt"
    logs_file = open(logs_path, "x")
    logs_file.close()
    log("Initializing")
    load_settings()
    init_schedule() 
    
    if settings.get("uuid") == None or settings.get("uuid") == "None":
        
        settings["uuid"] = uuid7()
        print(settings["uuid"])
    
    save_settings()
    log("Done initializing")
    
def init_schedule() -> None:
    """
    Sets up the initial schedule with tasks from the settings.
    """
    
    global sched
    
    log("Initialising schedule")
    
    #This goes through all days and executes schedule.every().""insert day"".at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
    for day in sched:
        
        for task in sched.get(day):
        
            getattr(schedule.every(), day.name).at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
            
    log("Done initialising schedule")
    
def execute_current_tasks():
    
    log("Checking for tasks to be done")
    schedule.run_pending()
    log("Current Tasks done")

def add_new_task_to_sched(weekday: Weekday, time : str, dispense_seconds: int) -> None:
    """
    Creates a new Task and adds it to the settings and current schdule
    TODO: Refactor loop into it's own function for code prettiness.
    """
    
    if not re.search("[0-2][0-4]:[0-5][0-9]",time):
        
        raise ValueError("Time must be a string of format hh:mm")
    
    if dispense_seconds < 0 or not type(dispense_seconds) == int:
        
        raise ValueError("dispense_seconds must be a positive int or 0")
    
    response = {"response" :"Invalid Input"}
    
    global settings
    global sched
    
    log("Adding task")
    log("Adding task to schedule variable")
    
    if weekday == Weekday.everyday:
        
        for day in sched:
            task = Task(time, dispense_seconds)
            response = add_new_task_to_day(task, sched.get(day), response)
            put_new_task_on_schedule(day, task)
    
    else:
        
        day = sched.get(weekday)
        response = add_new_task_to_day(Task(time, dispense_seconds), day, response)
        log("Done adding task to schedule variable")

    save_settings()
    schedule.clear()
    init_schedule()
    log("Done adding task")
    return json.dumps(response)
     
def add_new_task_to_day(task: Task, day: list[Task], response: str) -> str:
    
    was_added: bool = False
    
    log("Adding task to day list")
    
    for saved_task in day:
        
        if saved_task.same_task(task):
            
            if(task.dispense_seconds <= 0):
                
                day.remove(saved_task)
                was_added = True
                response.update({"response" :"Removed Task"})
                break
                
            saved_task.dispense_seconds = task.dispense_seconds
            was_added = True
            response.update({"response" :"Updated Task"})
            break
    
    if not was_added and task.dispense_seconds >0:
        
        day.append(task)
        response.update({"response" :"Added Task"})
        
    return response

def put_new_task_on_schedule(day: Weekday, task: Task) -> None:
    """
    Puts a new task on the current schedule.
    """

    log(f"Putting a new task on the schedule for {day.name}, {task.time} with {task.dispense_seconds} = {task.dispense_seconds}")
    
    #Equivilant to schedule.every()."insert day"..at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
    dispense_seconds: int = task.dispense_seconds
    time: str = task.time
    day_name: str = day.name
    getattr(schedule.every(), day.name).at(task.time).do(dispense,dispense_seconds = task.dispense_seconds)
    
    log("Done adding task to schedule")
    
def load_settings() -> None:
    """
    Loads the settings from settings.json and saves it into the global settings variable.
    """
    
    global settings
    
    log("Loading settings")
    
    if os.path.exists(settings_path):
        
        json_settings = open(settings_path, "r")
        
        if (os.path.getsize(settings_path) <= 0):
            
            log("settings.json doesn't exist")
            return
        
        settings = objectify_settings(json.load(json_settings))
        json_settings.close()
    
    else:
    
        json_settings = open(settings_path, "w")
        json_settings.close()
        
    log("Settings loaded")

def objectify_settings(settings_json: dict[str,any]) -> dict[str, any]:
    """
    Turns a settings json into a dictionary
    TODO: Make this not suck. Maybe even make this useless.
    """
    
    global settings
    
    log("Objectifieing settings")
    settings.update(settings_json)
    settings["schedule"] = objectify_schedule(settings_json.get("schedule"))
    log(f"Objectified settings: {settings}")
    return settings

def objectify_schedule(schedule_json: Json_sched) -> dict[Weekday, list[Task]]: 
    """
    Turns a schedule json into a dictionary
    TODO: Make this not suck. Maybe even make this useless.
    """
    
    global sched
    
    log("Objectifieing schedule")
    try:
        for day in schedule_json:

            dict_day = []
        
            for task in schedule_json.get(day):
            
                dict_day.append(Task(task.get("time"), int(task.get("dispense_seconds"))))
            
            sched.update({Weekday(int(day)):dict_day}) 
        
        log(f"Objectified schedule: {sched}")
        
    finally:
        
        return sched
    
def save_settings() -> None:
    """
    Sets the settings in settings.json.
    If the file doesn't exist it creates it.
    If the file exists it parses the settings, replaces unmatching ones and adds in non existent ones.
    """
    
    global settings
    
    log("Saving settings")
    
    if os.path.exists(settings_path):
        
        log("Settings.json found")
        settings_file = open(settings_path,"r")
        settings_file_string: str = settings_file.read()
        settings_file.close()
        
    else:
        
        log("Settings.json not found. Creating it.")
        _ = open(settings_path,"x")
        _.close()
        settings_file_string: str = ""
    
    if(settings_file_string == ""):
        
        log("Dumping settings to empty settings.json")
        settings_file = open(settings_path,"w")
        json.dump(dictify_settings(), settings_file, indent = 4)
        settings_file.close()
        log("Done dumping settings to empty settings.json")
        return

    log("Updating settings from settings.json")
    settings_json: dict[str, any] = json.loads(settings_file_string)
    settings_json.update(dictify_settings())
    log("Dumping updated settings to settings.json")
    settings_file = open(settings_path,"w")
    json.dump(settings_json, settings_file, indent = 2)
    log("Done Dumping updated settings to settings.json")
    
def dictify_settings() -> dict[str, any]:
    """
    Turns settings dictionary into a JSON
    TODO: Make this not suck. Maybe even make this useless.
    """
    
    log("Dictifieing settings")
    
    dictified_settings: dict[str, dict[int, list[dict[str,any]]]] = {}
    dictified_settings.update(settings)
    dictified_settings["schedule"] = dictify_schedule()
    uuid = settings.get("uuid")
    dictified_settings.update({"uuid": str(uuid)})
    log(f"Dictified settings {dictified_settings}")
    
    return dictified_settings
    
def dictify_schedule() -> Json_sched:
    """
    Turns schedule dictionary into a JSON compatible dict.
    TODO: Make this not suck. Maybe even make this useless.
    """
    
    global sched
    
    log("Dictifieing schedule")
    
    dictified_schedule: dict[int, list[dict[str,any]]] = {}
    
    for day, tasks in sched.items():
        
        dictified_day: list[dict[str,any]] = []
        
        for task in tasks:
            
            dictified_day.append(task.to_dict())
            
        dictified_schedule[day.value] = dictified_day
        
    log(f"Dictified schedule: {dictified_schedule}")
        
    return dictified_schedule

def dispense(dispense_seconds: int) -> None:
    """
    Turns the dispensing motor.
    """
    
    if dispense_seconds < 0 or not type(dispense_seconds) == int:
        
        raise ValueError("dispense_seconds must be a positive int or 0")
    
    log(f"Dispensing for {dispense_seconds} seconds")
    motor.forward()
    time.sleep(dispense_seconds)
    motor.stop()
    log(f"Done dispensing for {dispense_seconds} seconds")
    
def log(log_message: str):
    
    global logs_path
    
    time = f"{current_time.day}-{current_time.month}-{current_time.hour}-{current_time.minute}-{current_time.second}:"
    log_file = open(logs_path, "a")
    log_file.write(f"{time} {log_message}\n")
    log_file.close()