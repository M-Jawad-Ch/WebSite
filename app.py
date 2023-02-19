from flask import Flask, render_template, request, session, url_for, make_response, jsonify, redirect
from flask_cors import CORS
from flask_session import Session
from dotenv import load_dotenv
import os
from hashlib import md5


load_dotenv()
app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return 'Hello World'

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/verify', methods=['POST'])
def verify():
    params = request.get_json()

    if params['username'] == 'jawad' and md5(params['password'].encode()).hexdigest() == os.environ['admin_pass']:
        session['user'] = 'jawad'
        return redirect('/admin')
    else: return make_response(400)

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', default=None)
    return redirect('login')

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('login')
    return render_template('admin.html')

@app.route('/admin/<val>')
def admin_opts(val):
    if 'user' not in session:
        return redirect('login')

    if val not in ['publish']:
        return render_template('404.html')
    
    return render_template(val + '.html')

if __name__ == '__main__':
    app.secret_key = os.environ['session_secret_key']
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    app.run(debug=True)