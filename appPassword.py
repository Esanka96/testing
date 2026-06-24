import smtplib
from email.message import EmailMessage

# Email details
sender_email = 'sl1047@innodata.com'
receiver_email = 'sl1045@innodata.com'
subject = 'Test Email'
body = 'This is a test email.'

# App password generated from your Office 365 account
app_password = 'zsygvwdxtyvddmqs'

# Create a new email message
msg = EmailMessage()
msg['Subject'] = subject
msg['From'] = sender_email
msg['To'] = receiver_email
msg.set_content(body)

# Connect to Office 365 SMTP server
smtp_server = 'smtp.office365.com'
smtp_port = 587

try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        print('Email sent successfully!')
except Exception as e:
    print(f'Error: {e}')
