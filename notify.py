import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate
from user_database import connect
from datetime import *
import pymysql
import os 

recipient = ["aleung4@wisc.edu", "joe.wedderspoon@wisc.edu", "bridget.bartell@wisc.edu", "jennifer.kuo@wisc.edu"]

def get_day(count_back_days): 
	today = date.today()
	deadline = today - timedelta(days = count_back_days)

	return (deadline, today)

def query(COUNT_BACK_DAYS):
	# Connect to database 
	conn , c = connect()

	select_query = "SELECT * FROM entry WHERE date BETWEEN %s AND %s"
    
	c.execute(select_query, get_day(COUNT_BACK_DAYS))

	result = c.fetchall()

# Check date 

	# if not yet notified, notify. 
	
	# if notified longer than 5 days and no response, send again

	# if exist and still come up again, re-notify 

	# if notified and no response, re-notify 

	# if longer than 10 days & no reply & does not show up again, delete row 

	# if replied, deleted, not come up, delete in database

# Send email

""" Send a email to desired people """
def send_email(recipient):
    s = smtplib.SMTP(host='smtp.wiscmail.wisc.edu')

    file_name = '{}-amp_alert.txt'.format(date.today())
    email_name = "{}-amp_alert_report".format(date.today())
    msg = MIMEMultipart()

    msg['From'] = 'aleung4@wisc.edu'
    msg['To'] = recipient
    msg['Subject'] = email_name

    part = MIMEBase('application', "octect-stream")
    part.set_payload(open(file_name, "r").read().encode('utf-8'))
    part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(email_name))
    msg.attach(part)

    s.send_message(msg)
    
