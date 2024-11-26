from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
from flask_migrate import Migrate
import config
import routes
import models
from models import db

migrate = Migrate(app, db)


if __name__ == '__main__':
    app.run(debug=True)