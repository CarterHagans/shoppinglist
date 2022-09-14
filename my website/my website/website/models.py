from operator import inv
from tkinter.font import families
from . import db
from sqlalchemy.sql import func

class User(db.Model):
    _id =  db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(25))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    families = db.Column(db.String(1000))
    
    def __init__(self,name,email,password,families):
        self.name = name
        self.email = email
        self.password = password
        self.families = families

class Families(db.Model):
    _id =  db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(25))
    creator_name = db.Column(db.String(100))
    creator_email = db.Column(db.String(100))
    members = db.Column(db.String(1000))
    admins = db.Column(db.String(1000))
    shopping_list = db.Column(db.String(10000))
    inventory = db.Column(db.String(10000))
    num_of_items_list = db.Column(db.Integer)
    num_of_items_inventory = db.Column(db.Integer)
    list_audit_log = db.Column(db.String(10000))
    inventory_audit_log = db.Column(db.String(10000))
    
    def __init__(self,name,creator_name,creator_email,members,admins,shopping_list,inventory,num_of_items_list,num_of_items_inventory,list_audit_log,inventory_audit_log):
        self.name =name
        self.creator_name = creator_name
        self.creator_email = creator_email
        self.members =members
        self.admins = admins
        self.shopping_list =  shopping_list
        self.inventory = inventory
        self.num_of_items_list = num_of_items_list
        self.num_of_items_inventory = num_of_items_inventory
        self.list_audit_log = list_audit_log
        self.inventory_audit_log = inventory_audit_log