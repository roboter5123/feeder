from flask import Flask, request, render_template
import lib
import threading
from Weekday import Weekday
import socket_server as socks
app = Flask(__name__, template_folder='templates', static_folder='staticFiles')


@app.route('/')
def get_index() -> any:
    
    return render_template("index.html")

@app.route('/settings', methods = ["POST", "GET"])
def http_send_settings() -> dict[str, any]:
    
    if request.method == "GET":
        
        lib.log(f"Sending settings back to {request.remote_addr}")
        return lib.dictify_settings()
    
    elif request.method == "POST":
        
        lib.log(f"Setting settings to {request.json}")
        settings = request.json
        lib.save_settings()
        lib.load_settings()
        return lib.dictify_settings()

@app.route('/add-task', methods = ["POST", "GET"])
def http_add_task():
    
    if request.method == "GET":
        
        weekday = int(request.args.get("day"))
        time = request.args.get("time")
        dispense_seconds = int(request.args.get("amount"))
        return lib.add_new_task_to_sched(Weekday(weekday), time, dispense_seconds)

    elif request.method == "POST":
        
        requestjson = request.json
        weekday = requestjson.get("day")
        time = requestjson.get("time")
        dispense_seconds = int(requestjson.get("amount"))
        return lib.add_new_task_to_sched(Weekday(weekday), time, dispense_seconds)

@app.route("/dispense")
def http_dispense_seconds():
    
    lib.dispense(int(request.args.get("amount")))
    return {"dispensed": True}

if __name__ == '__main__':
    """
    Creates a second thread that runs the main loop of the machine.
    Then runs the flask api server for incoming orders.
    """
    
    lib.init()
    main_thread = threading.Thread(target=lib.main, daemon=True)
    main_thread.start()
    socket_thread = threading.Thread(target=socks.start_sockets)
    socket_thread.start()
    
    app.run()

    