from dotenv import load_dotenv
from flask_cors import CORS
from flask import Flask
from Modules.databasehandler import DbHandler
from os import environ

load_dotenv()

app = Flask(__name__)
CORS(app)

dbHandler = DbHandler('database.db')
app.secret_key = environ['session_secret_key']
app.config['SESSION_TYPE'] = 'filesystem'

session_duration = 15 * 60