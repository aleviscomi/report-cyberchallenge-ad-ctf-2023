import imp
from flask import Flask, g
from flask_mysqldb import MySQL
from code.frontend import frontend
import os



app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET', os.urandom(16))
app.config['MYSQL_HOST'] = os.environ.get('DBHOST', 'db')
app.config['MYSQL_USER'] = os.environ.get('DBUSER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('DBPASS', '')
app.config['MYSQL_DB'] = os.environ.get('DBSCHEMA', 'Capp')
app.config['DEBUG'] = os.environ.get('DEBUG', False)
app.config['max_file_size'] = 250

mysql = MySQL(app)

@app.before_request
def add_mysql():
    g.mysql = mysql.connection.cursor()

app.register_blueprint(frontend)