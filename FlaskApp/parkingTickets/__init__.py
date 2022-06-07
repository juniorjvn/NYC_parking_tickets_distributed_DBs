from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
# from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '47fa813e65eb0b390c0db262dda8c35c'
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}@localhost/nyc_open_data_manhattan"
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
# app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'jvn.pen.testing1@gmail.com'
# app.config['MAIL_PASSWORD'] = 'KAL12345KAL'
# mail = Mail(app)

from parkingTickets import route