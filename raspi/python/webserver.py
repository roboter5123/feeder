from flask import Flask, request, render_template
import lib
import threading
from Weekday import Weekday
app = Flask(__name__, template_folder='templates', static_folder='staticFiles')


@app.route('/')
def get_index() -> any:
    
    return render_template("index.html")

@app.route('/settings')
def http_send_settings() -> dict[str, any]:
    
    lib.log(f"Sending settings back to {request.remote_addr}")
    return lib.dictify_settings()

@app.route('/add-task')
def http_add_task():
    
    weekday = int(request.args.get("day"))
    time = request.args.get("time")
    dispense_seconds = int(request.args.get("amount"))
    
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
    
    main_thread = threading.Thread(target=lib.main, daemon=True)
    main_thread.start()
    socket_thread = threading.Thread(target=lib.start_sockets)
    socket_thread.start()
    
    app.run()

    