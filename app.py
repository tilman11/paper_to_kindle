import os
import re
from flask import (Flask, flash, request, redirect, 
    url_for, send_from_directory, send_file, render_template, after_this_request)
from werkzeug.utils import secure_filename
import subprocess
import time
# redis topics
from rq import Queue
from rq.job import Job
from worker import conn_cli
import requests

UPLOAD_FOLDER = './temp_files/upload'
ALLOWED_EXTENSIONS = {'pdf', }

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000  # 16 MB Uploadlimit

q = Queue(connection=conn_cli)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_command(auto_str: bool, out_marg: float, w: int, h: int):
    command = ''

    if auto_str:
        command += '-as'
    if out_marg is not None:
        if out_marg >= 0 and out_marg < 4:
            command += f'om {out_marg}'
        else:
            command += f'om {0.2}'
    if type(w) is int and type(h) is int:
        if w > 0 and h > 0:
            command += f'-w {w} -h {h}'

    return command.lstrip()


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file_info = {}
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # add to job qeue
            job = q.enqueue_call(
                func=transform_paper, args=(filename,), result_ttl=5000
            )
            print(job.get_id())
            return render_template('results.html', results=file_info)
            #return redirect(url_for('transform_to_kindle', filename=filename))
    return render_template('upload.html')


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn_cli)
    print(job.is_finished)
    job

    if job.is_finished:
        return str(job.result), 200
    else:
        return "Nay!", 202


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


def get_k2opt_metadata(output_text: str):
    # init retirn dict
    results = {
        'out_file_path': None,
        'file_size': None,
        'number_pages': None,
        'cpu_used': None,
    }
    # clean console tokens that are used for coloring the commandline output
    clean_output = re.sub(r"\[(\d+)[m]", "", output_text)
    # Extract path using regular expression
    results['out_file_path'] = re.findall(r"(?<=written to )(.+?_k2opt\.pdf)", clean_output)[0]
    results['out_filename'] = results['out_file_path'].split('/')[-1]
    results['file_size'] = re.findall(r"(?<=\()[0-9]\d*(\.\d+)?(?=\sMB\))", clean_output)[0]
    results['cpu_used'] = re.findall(r"(?<=CPU time used: )[1-9]\d*(\.\d+)?", clean_output)[0]

    return results


def transform_paper(filename):
    """_summary_

    Args:
        url (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        echo = subprocess.Popen(('echo'), stdout=subprocess.PIPE)
        transformation = subprocess.Popen(
            ["k2pdfopt", f"temp_files/upload/{filename}"],  #, "-ui-", "-om", "0.2", "-w 784", "-h 1135"], 
            stdin=echo.stdout,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE) 
    
        # Capture output and error together
        output, error = transformation.communicate()
        output_text = output.decode() + error.decode()  # Decode bytes to string
        file_info = get_k2opt_metadata(output_text)
        os.remove(f"temp_files/upload/{filename}")
        # file_info = {
        #     'out_file_path': 'temp_files/upload/2404.04988_onepager_local_k2opt.pdf',
        #     'out_filename': '2404.04988_onepager_local_k2opt.pdf',
        #     'file_size': 3.7,
        #     'number_pages': None,
        #     'cpu_used': 23.67,
        # }
        if file_info['out_file_path']:
            #return render_template('results.html', results=file_info)
            return file_info
        else:
            return "<h1>File Processing not possible</h1>"
    except Exception as e:
        print(f"Error in transform_paper(): {e}")
        return "<h1>File Processing failed!</h1>"
    

@app.route('/transform/kindle2/<filename>')
def transform_to_kindle(filename):
    try:
        echo = subprocess.Popen(('echo'), stdout=subprocess.PIPE)
        transformation = subprocess.Popen(
            ["k2pdfopt", f"temp_files/upload/{filename}"],  #, "-ui-", "-om", "0.2", "-w 784", "-h 1135"], 
            stdin=echo.stdout,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE) 
    
        # Capture output and error together
        output, error = transformation.communicate()
        output_text = output.decode() + error.decode()  # Decode bytes to string
        file_info = get_k2opt_metadata(output_text)
        os.remove(f"temp_files/upload/{filename}")
        # file_info = {
        #     'out_file_path': 'temp_files/upload/2404.04988_onepager_local_k2opt.pdf',
        #     'out_filename': '2404.04988_onepager_local_k2opt.pdf',
        #     'file_size': 3.7,
        #     'number_pages': None,
        #     'cpu_used': 23.67,
        # }
        if file_info['out_file_path']:
            return render_template('results.html', results=file_info)
        else:
            return "<h1>File Processing not possible</h1>"
    except Exception as e:
        print(f"Error running program: {e}")
        return "<h1>File Processing failed!</h1>"


@app.route('/download/<filename>')
def download(filename):
    path = f'temp_files/upload/{filename}'
    # TODO: find a way to delete files after download happend or limit the number of downloads!
    # @after_this_request
    # def remove_file(response):
    #     time.sleep(30)
    #     try:
    #         os.remove(path)
    #         file_handle.close()
    #     except Exception as error:
    #         app.logger.error("Error removing or closing downloaded file handle", error)
    #     return redirect('/', code=303)
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run()
