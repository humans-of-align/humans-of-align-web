''' IMPORTS '''

import pandas as pd
import numpy as np
import math

from flask import Flask, request, render_template, redirect, url_for, jsonify
import os
import gspread

'''
Get photo links for drive
'''


def edit_photo_links(df):
    links = df['Photo']
    for i in range(len(links)):
        dump, id = links[i].split('id=')
        new_link = 'https://drive.google.com/uc?export=view&id=' + id
        links[i] = new_link
    df['Photo'] = links
    return df


'''
Init flask app
'''
app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
sa = gspread.service_account(filename="humans-of-align.json")
sheet = sa.open("Render")

'''
READ FORM RESPONSES
'''
worksheet = sheet.worksheet("Sheet1")
records = worksheet.get_all_records()

'''
Landing page
'''


@app.route('/', methods=['GET', 'POST'])
def index():

    # Read google sheet
    sheet = sa.open("Render")
    worksheet = sheet.worksheet("Sheet1")
    records = worksheet.get_all_records()

    # Read dataframe
    df = pd.DataFrame.from_records(records)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.sort_values(by='Timestamp', ascending=False)
    # print(df)

    # Get links to photos
    df = edit_photo_links(df)

    # Pick recent 5 for carousal
    recent_five = df.head(5)
    recent_five_dict = recent_five.to_dict('list')
    # print(recent_five_dict)

    return render_template("index.html", recent_five=recent_five_dict)


'''
List of students page
'''


@app.route('/stories', methods=['GET', 'POST'])
def stories():

    # Read form responses
    sheet = sa.open("Render")
    worksheet = sheet.worksheet("Sheet1")
    records = worksheet.get_all_records()

    # Read dataframe
    df = pd.DataFrame.from_records(records)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.sort_values(by='Timestamp', ascending=False)
    # print(df)

    # Get links to photos
    df = edit_photo_links(df)

    students_details_dict = df.to_dict('list')

    rows = math.ceil(len(df['First Name'])/3)
    total = len(df['First Name'])
    start = 0
    index_list = []
    for i in range(rows):
        temp_list = []
        for j in range(3):
            if (start < total):
                temp_list.append(start)
                start += 1
        index_list.append(temp_list)

    index_list_normal = []
    for i in range(total):
        index_list_normal.append(i)

    return render_template("students.html", students_details=students_details_dict, index_list=index_list, index_list_normal=index_list_normal)


'''
Individual stories page
'''


@app.route('/stories/<name>', methods=['GET', 'POST'])
def students_name(name):

    # Read form responses
    sheet = sa.open("Render")
    worksheet = sheet.worksheet("Sheet1")
    records = worksheet.get_all_records()

    # Read dataframe
    df = pd.DataFrame.from_records(records)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.sort_values(by='Timestamp', ascending=False)
    # print(df)

    # Get links to photos
    df = edit_photo_links(df)

    # Get student details
    first_name, last_name = name.split('-')
    student_details = df.loc[(df['First Name'] == first_name) & (
        df['Last Name'] == last_name)]
    student_details_dict = student_details.to_dict('list')

    return render_template("individual_story.html", student_details=student_details_dict)


'''
Align Master's Program Page
'''
@app.route('/alignmastersprogram', methods=['GET'])
def align_masters():
    return render_template("align_masters.html")

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port=5000, debug=True)
