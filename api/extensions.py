from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from celery import Celery

celery = Celery(__name__)

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
