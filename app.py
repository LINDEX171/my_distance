from flask import Flask, request, render_template, jsonify
from math import sqrt
from datetime import datetime

app = Flask('my_distance')

distances = list()


def parse_point(raw):
    parts = raw.split(',')
    if len(parts) != 2:
        raise ValueError
    return [int(parts[0]), int(parts[1])]


@app.route('/', methods=['GET', 'POST'])
def html_calculate():
    if request.method == 'GET':
        return render_template('index.html', result=None, error=None)
    if request.method == 'POST':
        try:
            start_point = parse_point(request.form['start_point'])
            end_point = parse_point(request.form['end_point'])
        except (ValueError, KeyError):
            return render_template('index.html', result=None, error="Format invalide. Utilisez x,y (ex: 3,4).")
        distance = sqrt((end_point[1] - start_point[1])**2 + (end_point[0] - start_point[0])**2)
        result = {
            'requested_at': datetime.now(),
            'result_distance': distance,
            'start_point': start_point,
            'end_point': end_point
        }
        distances.append(result)
        return render_template('index.html', result=result, error=None)


@app.route('/api')
def index():
    return {}


@app.route('/api/distances')
def already_calculated():
    return list(distances)


@app.route('/api/distance', methods=['POST'])
def calculate():
    try:
        start_point = parse_point(request.json['start_point'])
        end_point = parse_point(request.json['end_point'])
    except KeyError as e:
        return jsonify({'error': f'Champ manquant : {e.args[0]}'}), 400
    except ValueError:
        return jsonify({'error': 'Format invalide. Utilisez "x,y" (ex: "3,4").'}), 400
    distance = sqrt((end_point[1] - start_point[1])**2 + (end_point[0] - start_point[0])**2)
    result = {
        'requested_at': datetime.now(),
        'result_distance': distance,
        'start_point': start_point,
        'end_point': end_point
    }
    distances.append(result)
    return jsonify(result)
