from flask import Flask, render_template, request, send_file
from flask_cors import CORS
import os
import csv
import omr_processing
import pandas as pd

app = Flask(__name__)

CORS(app, expose_headers=["x-suggested-filename"])

app.config['SECRET_KEY'] = 'zxcvbnm'
app.config['UPLOAD_FOLDER'] = 'static/omr_sheets'
app.config['UPLOAD_FOLDER1'] = 'static/answer'

curr = "dev"
if (curr=="dev"):
    @app.route('/')
    def home():
        messagehome = "defined"
        f = os.listdir("static/omr_sheets/")
        for i in f:
            fpath = os.path.join(('static/omr_sheets/'), str(i))
            if(os.path.isfile(fpath)):
                os.remove(fpath)
        f = os.listdir("static/answer/")
        for i in f:
            fpath = os.path.join(('static/answer/'), str(i))
            if(os.path.isfile(fpath)):
                os.remove(fpath)        
        filepath = "static/result/ans.csv"
        if(os.path.isfile(filepath)):
            os.remove(filepath)
        
        return render_template("index.html", messagehome=messagehome)
else:
    @app.route('/')
    def home():
        return render_template("maintenance.html")
@app.route('/upload',methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        files = request.files.getlist('file[]')
        # file1 = request.files.getlist('file[]').read()
        if (files[0].filename==''):
            val = "notdefined"
            message1 = "No File Selected"
            return render_template('index.html', message1=message1, val=val)

        else:

            for file in files:
                valn = "defined"
                msg = file.filename
                fmsg = msg.split('.')
                if(fmsg[1] == "csv"):
                    path = os.path.join(app.config['UPLOAD_FOLDER1'], file.filename)
                    file.save(path)
                else:
                    fmsgval = "defined"
                    message1 = "Upload file with .csv extension"
                    return render_template('index.html', message1=message1, fmsgval=fmsgval)
            message1 = "Uploaded Successfully"
            return render_template('index.html', message1=message1, valn=valn)
    # return render_template("index.html")


@app.route('/scan',methods=['GET','POST'])
def scan():
    if request.method == 'POST':
        files = request.files.getlist('file[]')
        if (files[0].filename == ''):
            valnn = "notdefined"
            message1 = "No File Selected"
            return render_template('index.html', message1=message1, valnn=valnn)
        else:
            valnnn = "defined"
            for file in files:
                s = file.filename
                fname = s.split('.')
                l=len(fname)
                if(fname[l-1]=="jpg" or fname[l-1]=="jpeg" or fname[l-1]=="png"):
                    path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(path)
                else:
                    msgval = "Defined"
                    message = "Upload file with extension .jpg .jpeg or .png"
                    return render_template('index.html', message=message, msgval=msgval)
            message = "Uploaded Successfully"
            return render_template('index.html', message=message, valnnn=valnnn)
    # return render_template("index.html")

@app.route('/result' ,methods=['GET','POST'])
def results():
    if request.method == 'POST':
        # global count
        
        omrpath = os.listdir("static/omr_sheets/")
        answerpath = os.listdir("static/answer/")

        if (len(omrpath)!=0 and len(answerpath)!=0):
            filepath = "static/result/ans.csv"
            csv_file = os.listdir("static/answer/")
            csv_path = "static/answer/" + str(csv_file[0])
            df = pd.read_csv(csv_path)
            qno = df.qno.to_list()
            q=len(qno)
            if(q==20):
                omr_processing.omr_calculation()
            elif(q==30):
                omr_processing.omr_calculation_1()
            else:
                message3 = "Please Check No Of Question in OMR or Answer Sheet"
                return render_template("index.html", message3=message3)
            with open(filepath) as csv_file:
                data = csv.reader(csv_file, delimiter=',')
                first_line = True
                files = []
                for row in data:
                    if not first_line:
                        files.append({
                            "roll": row[0],
                            "score": row[1],
                        })
                    else:
                        first_line = False
            return render_template("result.html",files=files)
        else:
            message3 = "Upload OMR & Answer Sheets"
            return render_template("index.html", message3=message3)

@app.route('/return-files/')
def return_files_tut():
    filepath = "static/result/ans.csv"

    res = send_file(filepath,  mimetype='application/x-csv', as_attachment=True, conditional=False, attachment_filename='report.csv')
    res.headers["x-suggested-filename"] = "result.csv"
    return res
@app.route('/return-app/')
def return_app_tut():
    filepath = "static/app/app-debug.apk"
    res = send_file(filepath,  mimetype='application/x-csv', as_attachment=True, conditional=False, attachment_filename='OMR Scanner.apk')
    res.headers["x-suggested-filename"] = "OMR Scanner.apk"
    return res
@app.route('/return-csv-sample/')
def return_csv_tut():
    filepath = "static/csv/CSV_Sample.csv"
    res = send_file(filepath,  mimetype='application/x-csv', as_attachment=True, conditional=False, attachment_filename='CSV_Sample.csv')
    res.headers["x-suggested-filename"] = "CSV_Sample.csv"
    return res
@app.route('/return-omr/')
def return_omr_tut():
    filepath = "static/omr/OMR_Sample.jpg"
    res = send_file(filepath,  mimetype='application/x-csv', as_attachment=True, conditional=False, attachment_filename='OMR_Sample.jpg')
    res.headers["x-suggested-filename"] = "OMR_Sample.jpg"
    return res

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(debug=True, host='0.0.0.0')
