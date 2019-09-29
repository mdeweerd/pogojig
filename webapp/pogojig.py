#!/usr/bin/env python3

# TODO setup webserver user disk quota

import tempfile
import uuid
from functools import wraps
from os import path
import os
import sqlite3

from flask import Flask, url_for, redirect, session, make_response, render_template, request, send_file, abort, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms.fields import RadioField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename

from job_queue import JobQueue

app = Flask(__name__, static_url_path='/static')
app.config.from_envvar('POGOJIG_SETTINGS')

class UploadForm(FlaskForm):
    upload_file = FileField(validators=[DataRequired()])

class ResetForm(FlaskForm):
    pass

job_queue = JobQueue(app.config['JOB_QUEUE_DB'])

def tempfile_path(namespace):
    """ Return a path for a per-session temporary file identified by the given namespace. Create the session tempfile
    dir if necessary. The application tempfile dir is controlled via the upload_path config value and not managed by
    this function. """
    sess_tmp = path.join(app.config['UPLOAD_PATH'], session['session_id'])
    os.makedirs(sess_tmp, exist_ok=True)
    return path.join(sess_tmp, namespace)

def require_session_id(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        return fun(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/jigerator')
@require_session_id
def jigerator():
    forms = { 'svg_form': UploadForm(), 'reset_form': ResetForm() }

    if 'render_job' in session:
        job = job_queue[session['render_job']]
        if job.finished:
            if job.result != 0:
                flash(f'Error processing SVG file', 'success') # FIXME make this an error, add CSS
            del session['render_job']

    r = make_response(render_template('jigerator.html', has_renders=path.isfile(tempfile_path('output.zip')), **forms))
    if 'render_job' in session:
        r.headers.set('refresh', '10')
    return r

# NOTES about the SVG file upload routines
#  * The maximum upload size is limited by the MAX_CONTENT_LENGTH config setting.
#  * The uploaded files are deleted after a while by systemd tmpfiles.d
# TODO: validate this setting applies *after* gzip transport compression

def render():
    if 'render_job' in session:
        job_queue[session['render_job']].abort()
    session['render_job'] = job_queue.enqueue('render',
            session_id=session['session_id'],
            client=request.remote_addr)

@app.route('/upload/svg', methods=['POST'])
@require_session_id
def upload_svg():
    upload_form = UploadForm()
    if upload_form.validate_on_submit():
        f = upload_form.upload_file.data
        f.save(tempfile_path('input.svg'))
        session['filename'] = secure_filename(f.filename) # Cache filename for later download

        render()
        flash(f'SVG file successfully uploaded.', 'success')
    else:
        flash(f'Error uploading SVG file: {"; ".join(msg for elem in upload_form.errors.values() for msg in elem)}', 'error')
    return redirect(url_for('jigerator'))

@app.route('/render/download/<path:file>')
def render_download(file):
    if file not in ['jig.stl', 'pcb_shape.dxf', 'kicad.zip', 'sources.zip',
            'kicad/jig-cache.lib', 'kicad/jig.kicad_pcb', 'kicad/jig.pro', 'kicad/jig.sch']:
        abort(404)

    return send_file(tempfile_path(file),
            mimetype='application/zip',
            as_attachment=True,
            attachment_filename=f'{path.splitext(session["filename"])[0]}_{path.basename(file)}')

@app.route('/pogojig_template_empty.svg')
def static_template():
    return send_file('static/pogojig_template_empty.svg',
            mimetype='application/octet-stream',
            as_attachment=True,
            attachment_filename='pogojig_template_empty.svg')

@app.route('/session_reset', methods=['POST'])
@require_session_id
def session_reset():
    if 'render_job' in session:
        job_queue[session['render_job']].abort()
    session.clear()
    flash('Session reset', 'success');
    return redirect(url_for('jigerator'))

