import random
import barcode
from barcode import EAN13
# import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from werkzeug import security
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from CWKdb_schema import db, Organiser, Attendee, Event, Ticket, Comment
from markupsafe import escape

#organiser: pqv5lt , attendee: svm39js
#
from flask_mail import Mail

# create the Flask app
from flask import Flask, render_template, request, redirect, url_for, make_response

app = Flask(__name__)
app.config['MAIL_SUPPRESS_SEND'] = False # Remember to change

# select the database filename
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///todo.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = "blablabla"
mail = Mail(app)

import os
# init the database so it can connect with our app
db.init_app(app)

# change this to False to avoid resetting the database every time this app is restarted
resetdb = True
if resetdb:
    with app.app_context():
        # drop everything, create all the tables, then put some data into the tables
        db.drop_all()
        db.create_all()
      



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    user_id = int(user_id)
    if Organiser.query.get(user_id):   #if the user is an organsier this will give a non-None value and hence the return will happen.
        return Organiser.query.get(user_id)
    elif Attendee.query.get(user_id):
        return Attendee.query.get(user_id)
    else:
        return None


#route to the indexOrganiser
@app.route('/indexOrganiser')
@login_required
def indexOrganiser():
    #MyOrganiser_id = current_user.id
    allevents = Event.query.filter().all()
    EventID = request.args.get("id")
    Eventdetails = Event.query.filter(Event.id==EventID).all()
    AllAttendees = Attendee.query.all()
    

    return render_template('indexOrganiser.html', eventshtml=allevents, eventdetailshtml=Eventdetails, attendeeshtml=AllAttendees)

#route to the indexAttendee
@app.route('/indexAttendee')
@login_required
def indexAttendee():
    Myattendee_id = current_user.id
    Mytickets = Ticket.query.filter(Ticket.attendee_id==Myattendee_id)
    allevents = Event.query.filter().all()
    EventID = request.args.get("id")
    Eventdetails = Event.query.filter(Event.id==EventID).all()
    return render_template('indexAttendee.html', eventshtml=allevents, eventdetailshtml=Eventdetails, myticketshtml=Mytickets,)


@app.route('/')
def start():
   return render_template('login.html')

@app.route('/login')
def login():
   allevents = Event.query.filter().all()
   EventID = request.args.get("id")
   Eventdetails = Event.query.filter(Event.id==EventID).all()
   return render_template('login.html', eventshtml=allevents, eventdetailshtml=Eventdetails)

@app.route('/loginActionAttendee', methods=['POST'])
def loginActionAttendee():
    username1 = request.form['username']
    password1 = request.form['password']

    DBusername = Attendee.query.filter_by(username=username1).first()
    if DBusername is None:
        return redirect(url_for('login'))
    if not security.check_password_hash(DBusername.password, password1):
        return redirect(url_for('login'))
    login_user(DBusername)

    return redirect(url_for('indexAttendee'))



@app.route('/loginActionOrganiser', methods=['POST'])
def loginActionOrganiser():
    username1 = request.form['username']
    password1 = request.form['password']

    DBusername = Organiser.query.filter_by(username=username1).first()
    if DBusername is None:
        return redirect(url_for('login'))
    if not security.check_password_hash(DBusername.password, password1):
        return redirect(url_for('login'))
    login_user(DBusername)
    #we are just setting the session where the user id is our id that corresponds to the id in user class in dbschema, via using login manager functionality
    return redirect(url_for('indexOrganiser'))



@app.route('/register', methods=['POST', 'GET'])
def register():
    return render_template('registration.html')
    #return redirect(url_for("registration")) 

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/registrationActionAttendee', methods=['POST', 'GET'])
@login_required
def registrationActionAttendee():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        email=request.form['email']

        password_hash=security.generate_password_hash(password)

        newuser = Attendee(username=username, password=password_hash, email=email)  #last thing is always user if which for now is static at 1
        db.session.add(newuser)
        db.session.commit()
        
        username1 = request.form['username']
        DBusername = Attendee.query.filter_by(username=username1).first()
        #login_user(DBusername)
        recipients = [email]
        sender = f"{os.getlogin()}@dcs.warwick.ac.uk"
        mail.send_message(sender=("NOREPLY",sender),subject="Giginator verfication code",body='The verification code is svm39js',recipients=recipients)
        return redirect(url_for('AttendeeVerification'))




@app.route('/AttendeeVerification', methods=['POST', 'GET'])
def AttendeeVerification():
    return render_template('AttendeeVerification.html')

@app.route('/submitverificationAttendee', methods=['POST', 'GET'])
def submitverificationAttendee():
    username = request.form['username']
    code = request.form['code']
    if (code!="svm39js"):
          return redirect(url_for('login'))
    DBusername = Attendee.query.filter_by(username=username).first()
    login_user(DBusername)
    return redirect(url_for('indexAttendee'))

@app.route('/registrationActionOrganiser', methods=['POST', 'GET'])
def registrationActionOrganiser():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        email=request.form['email']
        code1=request.form['code']
        if (code1!="Dc5_G1gz"):
          return redirect(url_for('register'))
        password_hash=security.generate_password_hash(password)

        newuser = Organiser(username=username, password=password_hash, email=email)  #last thing is always user if which for now is static at 1
        db.session.add(newuser)
        db.session.commit()
        
        username1 = request.form['username']
        DBusername = Organiser.query.filter_by(username=username1).first()
        #login_user(DBusername)
        recipients = [email]
        sender = f"{os.getlogin()}@dcs.warwick.ac.uk"
        mail.send_message(sender=("NOREPLY",sender),subject="Giginator verfication code",body='The verification code is pqv5lt' ,recipients=recipients)
        return redirect(url_for('OrganiserVerification'))


@app.route('/OrganiserVerification', methods=['POST', 'GET'])
def OrganiserVerification():
    return render_template('OrganiserVerification.html')

@app.route('/submitverificationOrganiser', methods=['POST', 'GET'])
def submitverificationOrganiser():
    username = request.form['username']
    code = request.form['code']
    if (code!="pqv5lt"):
          return redirect(url_for('login'))
    DBusername = Organiser.query.filter_by(username=username).first()
    login_user(DBusername)
    return redirect(url_for("indexOrganiser"))


@app.route('/newevent', methods=['POST'])
@login_required
def newevent():
   eventname = escape (request.form.get('eventname'))
   eventdate = escape (request.form.get('datename'))
   eventtime = escape (request.form.get('timename'))
   eventduration = escape (request.form.get('durationname'))
   eventcapacity = escape (request.form.get('capacityname'))
   eventlocation = escape (request.form.get('locationname'))

   qrytext = text("INSERT INTO EVENTS (name, date, time, duration, capacity, location, tickets, message) VALUES (:eventname, :datename, :timename, :durationname, :capacityname, :locationname, :ticketsname, :messagename);")
   qry = qrytext.bindparams(eventname = eventname, datename = eventdate, timename = eventtime, durationname = eventduration, capacityname = eventcapacity, locationname = eventlocation, ticketsname=0, messagename="")
   db.session.execute(qry)
   db.session.commit()
   return redirect(url_for("indexOrganiser"))

@app.route('/removeevent', methods=['POST'])
@login_required
def removeevent():
    eventid = escape (request.form.get('eventid'))
    eventname = Event.query.filter(Event.id==eventid).first()
    eventTickets = Ticket.query.filter(Ticket.event_id==eventid).all() # tickets that have been bought for the event
    #each event we have multiple tickets and we need a list of attendees of this tickets.
    qrytext = text("DELETE FROM EVENTS WHERE id=:eventid;")
    qry = qrytext.bindparams(eventid=eventid)
    db.session.execute(qry)
    qrytext2 = text('UPDATE TICKETS SET cancelled=:nowCancelled WHERE id=:eventid')
    qry2 = qrytext2.bindparams(nowCancelled="EVENT IS NOW CANCELLED", eventid=eventid)
    db.session.execute(qry2)
    db.session.commit()
    return redirect(url_for("indexOrganiser"))


    

@app.route('/promoteAttendee', methods=['POST'])
@login_required
def promoteAttendee():
    attendeeid = escape (request.form.get('attendeeid'))
    attendee = Attendee.query.filter(Attendee.id==attendeeid).first()

    if attendee is None:
        return "Error: Attendee not found."

    username1 = attendee.username
    password1 = attendee.password
    email1 = attendee.email
    qrytext = text("DELETE FROM ATTENDEES WHERE id=:attendeeid;")
    qry = qrytext.bindparams(attendeeid=attendeeid)
    db.session.execute(qry)

    qrytext2 = text("INSERT INTO ORGANISERS (username, password, email) VALUES (:newusername, :newpassword, :newemail);") 
    qry2 = qrytext2.bindparams(newusername=username1, newpassword=password1, newemail=email1)
    db.session.execute(qry2)
    db.session.commit()
    return redirect(url_for("indexOrganiser"))

@app.route('/commentsAttendee', methods=['GET', 'POST'])
@login_required
def commentsAttendee():
    eventID = request.args.get("event_id") 
    print(eventID)
    comments = Comment.query.filter(Comment.event_id==eventID).all()
    return render_template('commentsAttendee.html',event_id=eventID, commentshtml=comments)

@app.route('/newcomment', methods=['POST', 'GET'])
@login_required
def newcomment():
    attendee_id = current_user.id
    eventID = request.form['event']
    print(eventID)
    commentEntered = request.form['commentname'] #what we input from the form text
    print(commentEntered)
        
    qrytext = text("INSERT INTO COMMENTS (event_id, comment, attendee_id) VALUES (:event_id, :comment, :attendee_id);")
    qry = qrytext.bindparams(event_id = eventID, comment = commentEntered, attendee_id=attendee_id)
    db.session.execute(qry)
    db.session.commit()
    return redirect(url_for('commentsAttendee', event_id=eventID))















@app.route('/newticket', methods=['POST'])
@login_required
def newticket():
  eventID = escape (request.form.get('eventid'))
  attendeeID = current_user.id
  eventName = Event.query.filter(Event.id==eventID).first().name #might use 
  used_numbers = []
  cancelled = "EVENT NOT CANCELLED"
  while True:
     new_num = random.randint(100000, 1000000)
     if new_num not in used_numbers:
         used_numbers.append(new_num)
         break
  EAN = barcode.get_barcode_class('code128')
  Barcode = EAN(str(new_num)).render()
  qrytext = text("INSERT INTO TICKETS (event_id, event_name, attendee_id, barcode, cancelled) VALUES (:event_id, :event_name, :attendee_id, :barcode, :cancelled);")
  qry = qrytext.bindparams(event_id=eventID, event_name = eventName, attendee_id=attendeeID, barcode=Barcode, cancelled=cancelled)
  db.session.execute(qry)
  
  ticketsInc = (Event.query.filter(Event.id==eventID).first().tickets) + 1
  Capacity = (Event.query.filter(Event.id==eventID).first().capacity)
    
  percentage_sold = (ticketsInc / Capacity) * 100
  if (percentage_sold == 100):
     message = "FULL"
  elif (percentage_sold >= 95):
    remaining_capacity = Capacity - ticketsInc
    message = "last "++remaining_capacity++" spaces"
  else:
    message = ""
  
  qrytext2 = text('UPDATE EVENTS SET tickets=:ticketsInc, message=:newMessage WHERE id=:eventid')
  qry2 = qrytext2.bindparams(ticketsInc=ticketsInc, newMessage=message,  eventid=eventID)
  db.session.execute(qry2)
  db.session.commit()
  

  
  return redirect(url_for("indexAttendee"))



@app.route('/cancelticket', methods=['POST'])
@login_required
def cancelticket():
    ticketID = escape (request.form.get('ticketid'))
    eventID = Ticket.query.filter(Ticket.id==ticketID).first().event_id
    #attendeeID = current_user.id
    qrytext = text("DELETE FROM TICKETS WHERE id=:ticketID;")
    qry = qrytext.bindparams(ticketID=ticketID)
    db.session.execute(qry)
    
    ticketsDec = (Event.query.filter(Event.id==eventID).first().tickets) - 1
    
    Capacity = (Event.query.filter(Event.id==eventID).first().capacity)
    percentage_sold = (ticketsDec / Capacity) * 100
    if (percentage_sold == 100):
       message = "FULL"
    elif (percentage_sold >= 95):
      remaining_capacity = Capacity - ticketsDec
      message = "last "++remaining_capacity++" spaces"
    else:
      message = ""
  
    qrytext2 = text('UPDATE EVENTS SET tickets=:ticketsDec, message=:newMessage WHERE id=:eventid')
    qry2 = qrytext2.bindparams(ticketsDec=ticketsDec, newMessage=message,  eventid=eventID)
    db.session.execute(qry2)
    db.session.commit()
    return redirect(url_for("indexAttendee"))
