from flask import render_template, request, make_response, jsonify, redirect, send_from_directory
from hashlib import md5
from re import sub
from base64 import b64decode
from os import listdir
from Modules.databasehandler import Post, User, title_parser

from sqlalchemy.exc import IntegrityError

from init import app, dbHandler, session_duration


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/static/<val>', methods=['GET'])
def send_file(val):
    return send_from_directory( 'static', val )
    

@app.route('/verify', methods=['POST'])
def verify():
    params = request.get_json()

    username = params['username']; password = params['password']
    user:User = dbHandler.get(username, User)

    if user and user.password == md5(password.encode()).hexdigest():
        resp = redirect('/admin')
        resp.set_cookie('uname', 'jawad', max_age=session_duration)

        if user.admin:
            resp.set_cookie('main-auth', 'True')

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

@app.route('/posts/<url>', methods=['GET'])
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
    urls = listdir('static/images')
    return make_response(jsonify(urls))

if __name__ == '__main__':
    app.run(debug=True)