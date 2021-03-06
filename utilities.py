#This file contains helper functions which use the sql.py to perform routine operations 
#on users like adding them to database for first time or updating values.
from sql import Database, Table, Column

db=Database("data.db")

users=Table(db,"users",[Column("id","TEXT"),
    Column("email","TEXT"),
    Column("picture","TEXT"),
    Column("name","TEXT")])

def add_user(sub):
    users.add_element(sub)

def update_user(sub,values: dict):
    users.update(sub,values)
