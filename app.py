from flask import Flask, request, render_template
from math import sqrt
from datetime import datetime

app = Flask('my_distance')

distances = list()

@app.route('/', methods=['GET', 'POST'])
def html_calculate():
    if request.method == 'GET':
        return render_template('index.html', result=None)
    if request.method == 'POST':
        start_point = list(map(lambda x: int(x), request.form['start_point'].split(',')[0:2]))
        end_point = list(map(lambda x: int(x), request.form['end_point'].split(',')[0:2]))
        distance = sqrt((end_point[1] - start_point[1])**2 + (end_point[0] - start_point[0])**2)
        result = {
            'requested_at': datetime.now(),
            'result_distance': distance,
            'start_point': start_point,
            'end_point': end_point
        }
        distances.append(result)
        return render_template('index.html', result=result)

@app.route('/api')
def index():
    return {}

@app.route('/api/distances')
def already_calculated():
    return list(distances)

@app.route('/api/distance', methods=['POST'])
def calculate():
    start_point = list(map(lambda x: int(x), request.json['start_point'].split(',')[0:2]))
    end_point = list(map(lambda x: int(x), request.json['end_point'].split(',')[0:2]))
    distance = sqrt((end_point[1] - start_point[1])**2 + (end_point[0] - start_point[0])**2)
    result = {
        'requested_at': datetime.now(),
        'result_distance': distance,
        'start_point': start_point,
        'end_point': end_point
    }
    distances.append(result)
    return result
