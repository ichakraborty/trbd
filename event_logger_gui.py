"""
Flask app to log clinical events of interest for 
TRBD Clinical Trial with Baylor College of Medicine. 
Code is only to be used by medical students logging events
with patient during interactions. 

Code is not meant to be modified, altered, or copied
for any other purpose besides TRBD Clinical trial. 

@author  Isha Chakraborty
@version 1.3 04/07/2025
"""

import sys
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pandas as pd
import os

project_id = ""
if len(sys.argv) >= 2:
    project_id = sys.argv[1]

app = Flask(__name__)

time_stamp = datetime.now().strftime("%m%d_%H_%M")
output_folder = ""
if project_id == "":
    data_file = os.path.join(output_folder, f"event_log_{time_stamp}.csv")
else:
    data_file = os.path.join(output_folder, f"{project_id}_event_log_{time_stamp}.csv")

if not os.path.exists(data_file):
    df = pd.DataFrame(columns=["Event", "Start Date", "Start Time", "End Date", "End Time", "Notes"])
    df.to_csv(data_file, index=False, mode='w', header=True)

active_events = {}

def log_event(event_name, start_time, end_time, notes=""):
    end_date = end_time.strftime("%Y-%m-%d") if end_time else "N/A"
    end_time_str = end_time.strftime("%H:%M:%S") if end_time else "N/A"

    data = {
        "Event": event_name,
        "Start Date": start_time.strftime("%Y-%m-%d"),
        "Start Time": start_time.strftime("%H:%M:%S"),
        "End Date": end_date,
        "End Time": end_time_str,
        "Notes": notes
    }
    df = pd.DataFrame([data])
    df.to_csv(data_file, mode='a', header=False, index=False)
    print(f"Logged event to {os.path.abspath(data_file)}:")
    print(data)

@app.route('/toggle_event', methods=['POST'])
def toggle_event():
    data = request.get_json()
    event_name = data['event']
    notes = data.get('notes', '')

    if event_name in active_events:
        start_time = active_events.pop(event_name)
        log_event(event_name, start_time, datetime.now(), notes)
        return jsonify({"message": f"Ended {event_name}", "status": "Press a button to start an event", "active_event": None})
    else:
        active_events.clear()
        active_events[event_name] = datetime.now()
        return jsonify({"message": f"Started {event_name}", "status": f"{event_name} has started", "active_event": event_name})

@app.route('/abort_event', methods=['POST'])
def abort_event():
    data = request.get_json()
    notes = data.get('notes', '')
    event_name = next(iter(active_events), None)

    if event_name:
        start_time = active_events.pop(event_name)
        notes = f"ABORTED: {notes}" if notes else "ABORTED"
        log_event(event_name, start_time, None, notes)
        return jsonify({"message": f"Aborted {event_name}", "status": "Event Aborted", "active_event": None})
    else:
        return jsonify({"message": "No active event to abort.", "status": "No active event", "active_event": None})

@app.route('/')
def home():
    html_content = '''
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
            .controls {
                margin-top: 30px;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 10px;
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
            .btn5 { background-color: #e0bbff; }
            .btn6 { background-color: #fdfd96; }
            .btn7 { background-color: #c1f0f6; }
            .btn8 { background-color: #d3f8e2; }
            .btn9 { background-color: #f6d6ad; }
            .btn10 { background-color: #fbc4ab; }
            .abort-btn { background-color: #ff4444; color: white; width: 220px; height: 50px; }
            .notes-input { padding: 10px; font-size: 16px; width: 400px; border-radius: 10px; border: 1px solid #ccc; }
            .active { background-color: #32CD32 !important; color: white; }
        </style>
        <script>
            let currentEvent = null;
            let activeButton = null;

            function playBeep() {
                const context = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = context.createOscillator();
                oscillator.type = "sine";
                oscillator.frequency.setValueAtTime(1000, context.currentTime);
                oscillator.connect(context.destination);
                oscillator.start();
                setTimeout(() => oscillator.stop(), 300);
            }

            function getNotes() {
                return document.getElementById("notes").value;
            }

            function toggleEvent(eventName, button) {
                fetch('/toggle_event', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 'event': eventName, 'notes': getNotes() })
                }).then(response => response.json())
                  .then(data => {
                      document.getElementById("status").innerText = data.status;
                      if (activeButton && activeButton !== button) {
                          activeButton.classList.remove('active');
                      }
                      if (data.active_event === null) {
                          button.classList.remove('active');
                          document.getElementById("notes").value = "";
                      } else {
                          button.classList.add('active');
                          activeButton = button;
                      }
                      currentEvent = data.active_event;
                      playBeep();
                  });
            }

            function abortEvent() {
                if (!currentEvent) {
                    alert("No active event to abort.");
                    return;
                }

                fetch('/abort_event', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 'notes': getNotes() })
                }).then(response => response.json())
                  .then(data => {
                      document.getElementById("status").innerText = data.status;
                      if (activeButton) activeButton.classList.remove('active');
                      currentEvent = data.active_event;
                      document.getElementById("notes").value = "";
                      playBeep();
                  });
            }
        </script>
    </head>
    <body>
        ''' + (f'<div class="status">Project ID: {project_id}</div>' if project_id else '') + '''
        <div id="status" class="status">Press a button to start an event</div>
        <div class="container">
            <button class="btn1" onclick="toggleEvent('DBS Programming Session', this)">DBS Programming Session</button>
            <button class="btn2" onclick="toggleEvent('Clinical Interview', this)">Clinical Interview</button>
            <button class="btn3" onclick="toggleEvent('Lounge Activity', this)">Lounge Activity</button>
            <button class="btn5" onclick="toggleEvent('Surprise', this)">Surprise</button>
            <button class="btn6" onclick="toggleEvent('VR-PAAT', this)">VR-PAAT</button>
            <button class="btn7" onclick="toggleEvent('Sleep Period', this)">Sleep Period</button>
            <button class="btn8" onclick="toggleEvent('Meal', this)">Meal</button>
            <button class="btn9" onclick="toggleEvent('Social', this)">Social</button>
            <button class="btn10" onclick="toggleEvent('Break', this)">Break</button>
            <button class="btn4" onclick="toggleEvent('Other', this)">Other</button>
        </div>
        <div class="controls">
            <input type="text" id="notes" class="notes-input" placeholder="Enter optional notes (only while event active)..." />
            <button class="abort-btn" onclick="abortEvent()">Abort Current Event</button>
        </div>
    </body>
    </html>
    '''
    return html_content

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
