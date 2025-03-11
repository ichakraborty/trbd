'''
Flask app to log clinical events of interest for 
TRBD Clinical Trial with Baylor College of Medicine. 
Code is only to be used by medical students logging events
with patient during interactions. 

Code is not meant to be modified, altered, or copied
for any other purpose besides TRBD Clinical trial. 

@author  Isha Chakraborty
@version 1.0 03/11/2025

'''


from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pandas as pd
import os

app = Flask(__name__)

time_stamp = datetime.now().strftime("%m%d_%H_%M")
data_file = f"event_log_{time_stamp}.csv"

if not os.path.exists(data_file):
    df = pd.DataFrame(columns=["Event", "Start Date", "Start Time", "End Date", "End Time"])
    df.to_csv(data_file, index=False, mode='w', header=True)

active_events = {}

def log_event(event_name, start_time, end_time):
    data = {
        "Event": event_name,
        "Start Date": start_time.strftime("%Y-%m-%d"),
        "Start Time": start_time.strftime("%H:%M:%S"),
        "End Date": end_time.strftime("%Y-%m-%d"),
        "End Time": end_time.strftime("%H:%M:%S")
    }
    df = pd.DataFrame([data])
    df.to_csv(data_file, mode='a', header=False, index=False)
    
    print(f"Logged event to {os.path.abspath(data_file)}:")
    print(data)

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <style>
            body {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                background-color: #f0f8ff;
                font-family: Helvetica, sans-serif;
            }
            .status {
                font-size: 24px;
                margin-bottom: 20px;
                font-weight: bold;
            }
            .container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                text-align: center;
            }
            button {
                width: 200px;
                height: 100px;
                font-size: 20px;
                font-family: Helvetica, sans-serif;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .btn1 { background-color: #ffcccb; }
            .btn2 { background-color: #add8e6; }
            .btn3 { background-color: #90ee90; }
            .btn4 { background-color: #ffb6c1; }
            .active { background-color: #4CAF50 !important; color: white; }
        </style>
        <script>
            function playBeep() {
                var context = new (window.AudioContext || window.webkitAudioContext)();
                var oscillator = context.createOscillator();
                oscillator.type = "sine";
                oscillator.frequency.setValueAtTime(1000, context.currentTime);
                oscillator.connect(context.destination);
                oscillator.start();
                setTimeout(() => oscillator.stop(), 300);
            }
            function toggleEvent(eventName, button) {
                fetch('/toggle_event', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 'event': eventName })
                }).then(response => response.json())
                  .then(data => {
                      document.getElementById("status").innerText = data.status;
                      button.classList.toggle('active');
                      playBeep();
                  });
            }
        </script>
    </head>
    <body>
        <div id="status" class="status">Press a button to start an event</div>
        <div class="container">
            <button class="btn1" onclick="toggleEvent('DBS Programming Session', this)">DBS Programming Session</button>
            <button class="btn2" onclick="toggleEvent('Clinical Interview', this)">Clinical Interview</button>
            <button class="btn3" onclick="toggleEvent('Lounge Activity', this)">Lounge Activity</button>
            <button class="btn4" onclick="toggleEvent('Other', this)">Other</button>
        </div>
    </body>
    </html>
    '''

@app.route('/toggle_event', methods=['POST'])
def toggle_event():
    data = request.get_json()
    event_name = data['event']
    if event_name in active_events:
        end_time = datetime.now()
        start_time = active_events.pop(event_name)
        log_event(event_name, start_time, end_time)
        return jsonify({"message": f"Ended {event_name}", "status": "Press a button to start an event"})
    else:
        active_events[event_name] = datetime.now()
        return jsonify({"message": f"Started {event_name}", "status": f"{event_name} has started"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

