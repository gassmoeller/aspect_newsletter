#!/bin/python

import os
import requests
import datetime
import smtplib
from unidecode import unidecode

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

import sys
from time import strftime

def get_headers():
    # Create the header of the message (a plain-text and an HTML version).
    text_header = "Hello everyone!\n\nThis is ASPECT newsletter #" + str(number) + ".\nIt automatically reports recently merged features and discussions about the ASPECT mantle convection code.\n\n"
    html_header = """\
    <html>
      <head></head>
      <body>
        <p>Hello everyone!<br><br>
           This is ASPECT newsletter #""" + str(number) + ".<br>It automatically reports recently merged features and discussions about the ASPECT mantle convection code.<br>"
    
    return html_header,text_header

def get_pull_request_headers():
    # Create the header of the pull request part of the message (a plain-text and an HTML version).
    text_header = "\n## Below you find a list of recently proposed or merged features:\n\n"
    html_header = "<br>Below you find a list of recently proposed or merged features:<br><br>\n"
    return html_header,text_header

def get_issue_headers():
    # Create the header of the pull request part of the message (a plain-text and an HTML version).
    text_header = "\n## And this is a list of recently opened or closed discussions:\n\n"
    html_header = "<br>And this is a list of recently opened or closed discussions:<br><br>\n"
    return html_header,text_header

def get_footers():
    html_footer="""<br>A list of all major changes since the last release can be found at <a href="https://aspect.geodynamics.org/doc/doxygen/changes_current.html">this website</a>.
    <br><br>Thanks for being part of the community!<br><br>
    Let us know about questions, problems, bugs or just share your experience by visting our <a href="https://community.geodynamics.org/c/aspect">forum</a>, or by opening issues or pull requests on <a href="https://www.github.com/geodynamics/aspect">Github</a>.<br>
    Additional information can be found at our <a href="https://aspect.geodynamics.org/">official website</a>, and CIG's <a href="https://geodynamics.org/cig/software/aspect/">ASPECT website</a>.
        </p>
      </body>
    </html>
    """
    text_footer="""\nA list of all major changes since the last release can be found at https://aspect.geodynamics.org/doc/doxygen/changes_current.html.
\n\nThanks for being part of the community!\n\n
Let us know about questions, problems, bugs or just share your experience by visiting https://community.geodynamics.org/c/aspect, or by opening issues or pull requests at https://www.github.com/geodynamics/aspect.
Additional information can be found at https://aspect.geodynamics.org/, and https://geodynamics.org/cig/software/aspect/."""
    return html_footer,text_footer

def send_mail(html_mail,text_mail):
    # Now compose message to send:
    me = '"Rene Gassmoeller" <rene.gassmoeller@mailbox.org>'
    you = "aspect@community.geodynamics.org"
    #you = "r.gassmoeller@mailbox.org"
    
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "ASPECT Newsletter #" + str(number)
    msg['From'] = me
    msg['To'] = you
    msg['Date'] = formatdate()
    
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text_mail, 'plain')
    part2 = MIMEText(html_mail, 'html')
    
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    
    # Send the message via SMTP server.
    s = smtplib.SMTP_SSL('smtp.mailbox.org:465')
    s.login("r.gassmoeller@mailbox.org",pw)
    
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(me, you, msg.as_string())
    s.quit()
    
def traverse_prs(issues):
    pull_requests_body_html = ""
    pull_requests_body_text = ""
    
    for issue in issues:
        if 'pull_request' in issue:
            # Handle recently closed pull requests
            r = requests.get(issue['pull_request']['url'], auth=('token',token))
            pr = r.json()

            create_time = datetime.datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            merge_time = now - 2 * report_timespan
            if 'merged_at' in pr and pr['merged_at'] != None:
                merge_time = datetime.datetime.strptime(pr['merged_at'], '%Y-%m-%dT%H:%M:%SZ')
            
            # If created or merged within the last 14 days:
            if (now - create_time < report_timespan) or (now - merge_time < report_timespan):
                html_pr = '<a href="' + pr['_links']['html']['href'] + '">#' + str(pr['number']) + '</a>: ' + unidecode(pr['title']) + ' ('
                html_pr += 'proposed by ' + '<a href="' + pr['user']['html_url'] + '">' + pr['user']['login'] + '</a>'

                if now - merge_time < report_timespan:
                    html_pr += '; merged'
 
                html_pr += ')<br>\n'

                text_pr =  '#' + str(pr['number']) + ': ' + unidecode(pr['title']) + ' (' 
                text_pr += 'proposed by ' + pr['user']['login'] 

                if now - merge_time < report_timespan:
                    text_pr += '; merged'

                text_pr +=  ') ' + pr['_links']['html']['href'] + '\n\n'
                pull_requests_body_html = pull_requests_body_html + html_pr
                pull_requests_body_text = pull_requests_body_text + text_pr
    return pull_requests_body_html, pull_requests_body_text

def traverse_issues(issues):
    issues_body_html = ""
    issues_body_text = ""
    
    for issue in issues:
        if 'pull_request' not in issue:
            create_time = datetime.datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            closed_time = now - 2 * report_timespan
            if issue['closed_at'] != None:
                closed_time = datetime.datetime.strptime(issue['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
    
            # If merged within the last 14 days:
            if (now - create_time < report_timespan) or (now - closed_time < report_timespan):
                status_change="("
                if now - create_time < report_timespan:
                    status_change += "opened"
                    if now - closed_time < report_timespan:
                        status_change += " and "
                if now - closed_time < report_timespan:
                    status_change += "closed"
                status_change += ")"
                html_pr = '<a href="' + issue['html_url'] + '">#' + str(issue['number']) + '</a> ' + unidecode(issue['title']) + ' ' + status_change + '<br>\n'
                text_pr =  '#' + str(issue['number']) + ': ' + unidecode(issue['title']) + ' ' + status_change + ' ' + issue['html_url'] + '\n\n'
                issues_body_html = issues_body_html + html_pr
                issues_body_text = issues_body_text + text_pr
    return issues_body_html, issues_body_text

def handle_pull_requests(request):
    pull_requests_body_html = ""
    pull_requests_body_text = ""
    
    pull_requests = request.json()
    
    prs_page_html, prs_page_text = traverse_prs(pull_requests)
    pull_requests_body_html += prs_page_html
    pull_requests_body_text += prs_page_text
    
    # This handles older pull requests that do not show up on the first page of
    # closed pull requests
    next_request = request
    while 'next' in next_request.links:
        next_request = requests.get(next_request.links['next']['url'],auth=('token',token))
        pull_requests = next_request.json()
        prs_page_html, prs_page_text = traverse_prs(pull_requests)
        pull_requests_body_html += prs_page_html
        pull_requests_body_text += prs_page_text

    return pull_requests_body_html,pull_requests_body_text

def handle_issues(request):
    issues_body_html = ""
    issues_body_text = ""
    
    issues = request.json()
    
    issues_page_html, issues_page_text = traverse_issues(issues)
    issues_body_html += issues_page_html
    issues_body_text += issues_page_text
    
    # This handles older pull requests that do not show up on the first page of
    # closed pull requests
    next_request = request
    while 'next' in next_request.links:
        next_request = requests.get(next_request.links['next']['url'],auth=('token',token))
        issues = next_request.json()
        issues_page_html, issues_page_text = traverse_issues(issues)
        issues_body_html += issues_page_html
        issues_body_text += issues_page_text

    return issues_body_html,issues_body_text


# Set up all necessary data from files and directories
path = os.path.dirname(os.path.abspath(__file__))

# Access token for Github.
tokenfile = open(path+"/token","r")
token = tokenfile.readline()
# Remove trailing newline character
token = token[:-1]
tokenfile.close()

# Access for Mailbox.
pwfile = open(path+"/pw","r")
pw = pwfile.readline()
# Remove trailing newline character
pw = pw[:-1]
pwfile.close()

# Current newsletter index.
numberfile = open(path+"/number","r")
number = int(numberfile.readline())
numberfile.close()

# Check time since last newsletter
datefile = open(path + "/last_send","r")
last_date = str(datefile.readline())
datefile.close()

update_date = datetime.datetime.strptime(last_date[:-1],'%Y-%m-%d %H:%M:%S')
now = datetime.datetime.utcnow()
report_timespan = now - update_date

if report_timespan < datetime.timedelta(13.5):
    sys.exit()

# Handle recently closed issues and pull requests
# Note that all pull requests are also issues in the github API
# That is why a single request returns all the information we need
payload = {'state': 'all', 'since': update_date.isoformat()}
request = requests.get('https://api.github.com/repos/geodynamics/aspect/issues', auth=('token',token), params=payload)
pull_requests_body_html,pull_requests_body_text = handle_pull_requests(request)
issues_body_html,issues_body_text = handle_issues(request)

html_header,text_header = get_headers()
html_pr_header,text_pr_header = get_pull_request_headers()
html_issues_header,text_issues_header = get_issue_headers()

html_footer,text_footer = get_footers()

if (pull_requests_body_html != "") or (issues_body_html != ""):
    html_mail = html_header
    text_mail = text_header
    
    if (pull_requests_body_html != ""):
        html_mail += html_pr_header + pull_requests_body_html
        text_mail += text_pr_header + pull_requests_body_text
        
    if (issues_body_html != ""):
        html_mail += html_issues_header + issues_body_html
        text_mail += text_issues_header + issues_body_text
        
    html_mail += html_footer
    text_mail += text_footer  
    
    #print text_mail
    
    send_mail(html_mail,text_mail)
    
    numberfile = open(path+"/number","w")
    numberfile.write(str(number+1))
    numberfile.close()

    datefile = open(path + "/last_send","w")
    datefile.write(now.strftime('%Y-%m-%d %H:%M:%S'))
    datefile.close()
