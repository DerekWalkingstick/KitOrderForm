from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import create_engine, MetaData, Table, Integer, Column

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True) # 150 = Max length
    password = db.Column(db.String(150)) # 150 = Max length
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(150), unique=True)
    users = db.relationship('User')

class KitType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sap_code = db.Column(db.String(150), unique=True)
    display_name = db.Column(db.String(150))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    logo = db.Column(db.String(150))
    kit_types = db.relationship('KitType')
