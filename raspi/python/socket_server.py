import lib
import json
import socket
from Weekday import Weekday
import time

login_url:str = "192.168.0.2"
server: socket
server_functions = {}
port = 8058

def start_sockets():
    
    global server_functions
    
    server_functions = {"get" : get_settings, "set" : set_settings, "dispense" : dispense_from_connection, "add": add_task_from_connection}
    start_outgoing_socket()
    listen_for_instructions()
        
def start_outgoing_socket():
    
        global server
        
        print("connecting to server")
    
        while True:
            
            time.sleep(5)
            
            try:
            
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            except Exception as e:
            
                lib.log(e)
                continue
        
            try:
                print("connecting")
                server.connect((login_url, port))
                print("connected")

            except Exception as e:
            
                lib.log(e)
                continue
        
            print("Successfully connected")
            lib.log("Successfully connected to login server")
            return
                
def listen_for_instructions():
    
    global server
    
    while True:
        
        response = server.recv(1024).decode()
        response = response[0:(len(response)-2)]
        response = response.split("#")
        command = response[0]
        del response[0]
        args = response
        
        print("Command: " + command)
        print("Args: " + str(args))
        
        try:
            
            response = server_functions.get(command)(args)
            response += "\n"

        except Exception as e:
            
            response = str(e) + "\n"
        
        server.sendall(response.encode())

def set_settings(args: list) -> bool:
    
    global settings
    global sched
    
    new_settings = json.loads(args[0])
    print(new_settings)
    new_settings = lib.objectify_settings(new_settings)
    settings = new_settings
    sched = settings.get("schedule")
    lib.save_settings()
    lib.load_settings()
    print(settings)
    return str(True)

def get_settings(args: list) -> dict:
    
    return json.dumps(lib.dictify_settings())

def add_task_from_connection(args: list) -> bool:
    
    day = Weekday(int(args[0]))
    time = args[1]
    dispense_seconds = int(args[2])
    lib.add_new_task_to_sched(day,time,dispense_seconds)
    return str(True)

def dispense_from_connection(args: list) -> bool:
    
    lib.dispense(int(args[0]))
    return str(True)
        
