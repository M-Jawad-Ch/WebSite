from flask import Flask, render_template, request, session, url_for, make_response, jsonify, redirect
from flask_cors import CORS
from flask_session import Session
from dotenv import load_dotenv
import os
from hashlib import md5

from Modules.databasehandler import DbHandler, Post, title_parser

from sqlalchemy.exc import IntegrityError

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
    else: return make_response('', 404)

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

    opts = ['publish', 'view-all']

    if val not in opts:
        return render_template('404.html')
    
    return render_template(val + '.html')

@app.route('/admin-post/<val>', methods=['GET', 'POST', 'OPTIONS', 'DELETE'])
def admin_posts(val):
    if 'user' not in session:
        return redirect('login')
    
    opts = ['publish', 'get', 'update', 'update-title', 'get-all', 'delete']
    
    if val not in opts:
        return redirect('404.html')
    
    params = request.get_json()

    if val == 'publish':
        p = Post(params['title'], params['body'])
        try:
            dbHandler.insert(p)
        except IntegrityError:
            dbHandler.sess.rollback()
            return make_response(jsonify({'status':'failure'}), 400)
        
        return make_response(jsonify({'status':'success'}), 200)
    
    elif val == 'get':
        p = dbHandler.get(title_parser(params['title']))
        return make_response(jsonify({'url':p.url, 'title':p.title, 'body':p.body}))
    
    elif val == 'get-all':
        posts = dbHandler.get_all()
        return make_response(jsonify( [{'url':p.url, 'title':p.title, 'body':p.body} for p in posts] ))
    
    elif val == 'delete':
        dbHandler.delete(title_parser(params['title']))
        return make_response("", 200)

    elif val == 'update':
        dbHandler.update(title_parser(params['prev-title']), Post(params['title'], params['body']))
        return make_response("", 200)
    
    return make_response('Not found' , 404)


if __name__ == '__main__':
    app.secret_key = os.environ['session_secret_key']
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    dbHandler = DbHandler('database.db')
    app.run(debug=True)