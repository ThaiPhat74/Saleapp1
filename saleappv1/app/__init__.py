import cloudinary
from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'GHFGH&*%^$^*(JHFGHF&Y*R%^$%$^&*TGYGJHFHGVJHGY'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/saledbv?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 2
app.config["COMMENT_SIZE"] = 2


db = SQLAlchemy(app=app)
login = LoginManager(app=app)
cloudinary.config(
    cloud_name='dapaiwg8m',
    api_key='148148595677726',
    api_secret='XesKx4E4iRvPgXk_0brt3XFHvpo',
)