import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate
from datetime import *
import pymysql
import os

""" Send the report to the designated email """
def send_report():
    s = smtplib.SMTP(host='smtp.wiscmail.wisc.edu')
    file_name = '{}-amp_alert.txt'.format(date.today())
    email_name = "{}-amp_alert_report".format(date.today())
    msg = MIMEMultipart()

    msg['From'] = 'csoc-projects@cio.wisc.edu'
    msg['To'] = "csoc-amp-alerts@lists.wisc.edu"
    msg['Subject'] = email_name

    part = MIMEBase('application', "octect-stream")
    part.set_payload(open(file_name, "r").read().encode('utf-8'))
    part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(email_name))
    msg.attach(part)

    s.send_message(msg)

""" Send the crash report to the designated email """
def send_crash_report():
    s = smtplib.SMTP(host='smtp.wiscmail.wisc.edu')
    file_name = "{}-AMP_Crash_Log.txt".format(date.today())
    email_name = "{}-AMP_Crash_Log.txt".format(date.today())
    msg = MIMEMultipart()

    msg['From'] = 'csoc-projects@cio.wisc.edu'
    msg['To'] = "csoc-amp-alerts@lists.wisc.edu"
    msg['Subject'] = email_name

    part = MIMEBase('application', "octect-stream")
    part.set_payload(open(file_name, "r").read().encode('utf-8'))
    part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(email_name))
    msg.attach(part)

    s.send_message(msg)
