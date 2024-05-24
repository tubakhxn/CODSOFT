from flask import Flask, render_template, request, jsonify, make_response
import requests
import pandas as pd
from pj import call_fn

# webapp
app = Flask(__name__, template_folder='./')


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/get')
def get_from_api():
    query = request.args.get('msg')
    skills = query.split(',')
    skill = []
    for i in skills:
        print(i.strip())
        skill.append(i.strip())
    call_fn(skill)
    df = pd.read_csv('file.csv')
    #skills
    #print(df['course_name'])
    json_data = df['course_name'].tolist()
    return jsonify(json_data)

    try:
        response = requests.get(json_data)
        return response
    except Exception as e:
        print(e)

