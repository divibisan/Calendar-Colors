import httplib2

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client import tools


# *** AUTHORIZATION ***
FLOW = flow_from_clientsecrets('client_secrets.json',
                               scope='https://www.googleapis.com/auth/calendar')

storage = Storage('calendar.dat')
credentials = storage.get()
if credentials is None or credentials.invalid is True:
    credentials = tools.run_flow(FLOW, storage)

http = httplib2.Http()
http = credentials.authorize(http)

service = build(serviceName='calendar', version='v3', http=http)
# *** END AUTHORIZATION ***

# Print list of calendars
page_token = None
while True:
    calendar_list = service.calendarList().list(pageToken=page_token).execute()
    counter = 0
    for calendar_list_entry in calendar_list['items']:
        print(str(counter) + ": ", end="")
        print(calendar_list_entry['summary'])
        counter += 1
    page_token = calendar_list.get('nextPageToken')
    if not page_token:
        break

# Ask user to choose which calendar to work with by number
#  will keep asking until user inputs a number
while True:
    try:
        choice = input("Choose which calendar to read: ")
        choice = int(choice)
        break
    except ValueError:
        print("Please enter a number")

# Get the id number of the chosen calendar
cal_id = calendar_list['items'][int(choice)]['id']

# Print list of events in specific calendar
page_token = None
while True:
    events = service.events().list(calendarId=cal_id,
                                   pageToken=page_token).execute()
    for event in events['items']:
        print(event['summary'])
        page_token = events.get('nextPageToken')
    if not page_token:
        break
