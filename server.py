import os
import re
from flask import (Flask, flash, request, redirect, 
    url_for, send_from_directory, render_template)
#from flask_executor import Executor
#from flask_shell2http import Shell2HTTP
from werkzeug.utils import secure_filename
import subprocess

UPLOAD_FOLDER = './temp_files/upload'
ALLOWED_EXTENSIONS = {'pdf',}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000 # 16 MB Uploadlimit
 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_command(auto_str: bool, out_marg_:float, w: int, h:int):
    command = ''

    if auto_str:
        command += '-as'
    if out_marg is not None:
        if out_marg>=0 and out_marg<4:
            command += f'om {out_marg}'
        else:
            command += f'om {0.2}'
    if type(w) is int and type(h) is int:
        if w>0 and h>0:
            command += f'-w {w} -h {h}'

    return command.lstrip()


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        # -om 0.2 -w 784 and -h 1135
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            flash(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('transform_to_kindle', filename=filename))
    return render_template('upload.html')

@app.route('/upload')
def uploaded_files():
    return "<h1>Test</h1>"


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

def get_k2opt_metadata(output_text: str):
    # init retirn dict
    results = {
        out_file_path: None,
        file_size: None,
        number_pages: None,
        cpu_used: None,
    }
    # clean console tokens that are used for coloring the commandline output
    clean_output = re.sub(r"\[(\d+)[m]", "", output_text)
    # Extract path using regular expression
    results['out_file_path'] = re.findall(r"(?<=written to )(.+?_k2opt\.pdf)", output_text)[0]
    results['file_size'] = re.findall(r"(?<=\()[0-9]\d*(\.\d+)?(?=\sMB\))", output_text)[0]
    results['cpu_used'] = re.findall(r"(?<=CPU time used: )[1-9]\d*(\.\d+)?", output_text)[0]

    return results


@app.route('/transform/kindle2/<filename>')
def transform_to_kindle(filename):
    try:
        echo = subprocess.Popen(('echo'), stdout=subprocess.PIPE)
        transformation = subprocess.Popen(
            ["k2pdfopt", f"temp_files/upload/{filename}", "-ui-", "-om", "0.2"], 
            stdin=echo.stdout,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE) #"-w 784", "-h 1135"
    
        # Capture output and error together
        #process = subprocess.Popen([program_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = transformation.communicate()
        output_text = output.decode() + error.decode()  # Decode bytes to string
        
        # Extract path using regular expression
        with open('./out.txt', 'w', encoding='utf-8') as f:
            f.write(output_text)
        out_file_path = re.findall(r"(?<=written to )(.+?_k2opt\.pdf)", output_text)[0]
        if out_file_path:
            return "<h1>File Processed successfull! Here is your file  {{out_file_path}}</h1>"
        else:
            return "<h1>File Processing not possible</h1>"
    except Exception as e:
        print(f"Error running program: {e}")
        return "<h1>File Processing failed!</h1>"
    #transformation.wait()
    #subprocess.run() 