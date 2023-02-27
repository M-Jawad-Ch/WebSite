from flask import Flask, render_template, request, url_for, make_response, jsonify, redirect
from flask_cors import CORS
from dotenv import load_dotenv
import os
from hashlib import md5
from re import sub
from base64 import b64decode

from Modules.databasehandler import DbHandler, Post, User, title_parser

from sqlalchemy.exc import IntegrityError

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/verify', methods=['POST'])
def verify():
    params = request.get_json()

    username = params['username']; password = params['password']
    user:User = dbHandler.get(username, User)

    if user and user.password == md5(password.encode()).hexdigest():
        resp = redirect('/admin')
        resp.set_cookie('uname', 'jawad')

        if user.admin:
            resp.set_cookie('main-auth', True)

        return resp
    else: return make_response('', 404)

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    resp = redirect('login')
    resp.delete_cookie('uname')
    return resp

@app.route('/admin')
def admin():
    if 'uname' not in request.cookies.keys():
        return redirect('login')
    return render_template('admin.html')

@app.route('/posts/<url>')
def posts(url):
    url = sub(r'[^a-z\-]','', url.lower())

    data = dbHandler.get(url, Post)

    if not data:
        return render_template('404.html')
    
    return render_template('posts.html', data={'heading':data.title, 'body':data.body})

@app.route('/admin-post/<val>', methods=['GET', 'POST', 'OPTIONS', 'DELETE'])
def admin_posts(val):
    if 'uname' not in request.cookies.keys():
        return redirect('login')
    
    opts = ['publish', 'get', 'update', 'update-title', 'get-all', 'delete', 'upload']
    
    if val not in opts:
        return redirect('404.html')
    
    params = request.get_json()

    if val == 'publish':
        p = Post(params['title'], params['body'], "jawad")
        try:
            dbHandler.insert(p)
        except IntegrityError:
            dbHandler.sess.rollback()
            return make_response(jsonify({'status':'failure'}), 400)
        
        return make_response(jsonify({'status':'success'}), 200)
    
    elif val == 'get':
        p = dbHandler.get(title_parser(params['title']), Post)
        return make_response(jsonify({'url':p.url, 'title':p.title, 'body':p.body}))
    
    elif val == 'get-all':
        if 'main-auth' not in request.cookies.keys():
            posts = dbHandler.sess.query(Post).filter(Post.owner == request.cookies.get('uname'))
        else: posts = dbHandler.get_all(Post)
        return make_response(jsonify( [{'url':p.url, 'title':p.title, 'body':p.body, 'owner':p.owner} for p in posts] ))
    
    elif val == 'delete':
        dbHandler.delete(title_parser(params['title']), Post)
        return make_response("", 200)

    elif val == 'update':
        dbHandler.update(title_parser(params['prev-title']), Post(params['title'], params['body'], "jawad"), Post)
        return make_response("", 200)
    
    elif val == 'upload':
        blob:str = request.get_json()['data']
        blob = sub(r'.+base64,','', blob)
        blob = b64decode(blob)

        with open(f'static/images/{request.get_json()["file-name"]}', 'wb') as f:
            f.write(blob)

        return make_response('', 200)
    
    return make_response('Not found' , 404)

@app.route('/img-urls', methods=['POST','GET'])
def img_urls():
    urls = os.listdir('static/images')
    return make_response(jsonify(urls))

if __name__ == '__main__':
    app.secret_key = os.environ['session_secret_key']
    app.config['SESSION_TYPE'] = 'filesystem'
    dbHandler = DbHandler('database.db')
    app.run(debug=True)