
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Boolean, String, Integer, Text

from flask_login import UserMixin

# create the database interface
db = SQLAlchemy()




# a model of an organiser for the database
class Organiser(UserMixin, db.Model): #usermixin is passes to user login manager functionality
    __tablename__='organisers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)

    def __init__(self, username, password, email):  #this is a contructor method
        self.username=username
        self.password=password
        self.email=email


# a model of a user for the database
class Attendee(UserMixin, db.Model): #usermixin is passes to user login manager functionality
    __tablename__='attendees'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)

    def __init__(self, username, password, email):  #this is a contructor method
        self.username=username
        self.password=password
        self.email=email





# a model of an event for the database
class Event(UserMixin, db.Model):
    __tablename__='events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    date = db.Column(db.Text())
    time = db.Column(db.Text())
    duration = db.Column(db.Integer())
    capacity = db.Column(db.Integer())
    location = db.Column(db.Text())
    tickets = db.Column(db.Integer())
    message = db.Column(db.Text())

    def __init__(self, name, date, time, duration, capacity, location, tickets, message):
        self.name=name
        self.date=date
        self.time=time      
        self.duration=duration
        self.capacity=capacity
        self.location=location
        self.tickets=tickets
        self.message=message


class Ticket(db.Model):
    __tablename__='tickets'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer)
    event_name = db.Column(db.Text())
    attendee_id = db.Column(db.Integer)
    barcode = db.Column(db.Integer)
    cancelled = db.Column(db.Text())
    

    def __init__(self, event_id, event_name, attendee_id, barcode, cancelled):  #this is a contructor method
        self.event_id=event_id
        self.attendee_id=attendee_id
        self.eventname=event_name
        self.barcode=barcode
        self.cancelled=cancelled
        
class Comment(db.Model):
    __tablename__='comments'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer)
    comment = db.Column(db.Text())
    attendee_id = db.Column(db.Text())

    
    def __init__(self, event_id, comment, attendee_id):  #this is a contructor method
        self.event_id=event_id
        self.comment=comment
        self.attende_id=attendee_id


    


