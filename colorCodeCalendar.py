import httplib2

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client import tools

# Define service object as a global variable
service = ""


def main():
    # *** AUTHORIZATION ***
    global service
    flow = flow_from_clientsecrets('client_secrets.json',
                                   scope='https://www.googleapis.com/auth/calendar')
    storage = Storage('calendar.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid is True:
        credentials = tools.run_flow(flow, storage)
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build(serviceName='calendar', version='v3', http=http)
    # *** END AUTHORIZATION ***


    # Read in config file to get name/colorID associations
    name_color_dict = read_config('config.txt')
    print(name_color_dict)

    # Choose calendar and get calendar ID
    #cal_id = choose_calendar()
    cal_id = '614i74105o8hdn44cqgts47hlc@group.calendar.google.com'

    # Get all events in specific calendar, change color of chosen events
    page_token = None
    while True:
        events = service.events().list(calendarId=cal_id,
                                       pageToken=page_token).execute()
        for event in events['items']:
            summary = event['summary']
            event_id = event['id']
            # if matches criteria, change color
            if summary in name_color_dict:
                set_event_color(cal_id, event_id, name_color_dict[summary])
            page_token = events.get('nextPageToken')
        if not page_token:
            break


def set_event_color(cal_id, event_id, color_id):
    # Sets the color of the specified event
    event = service.events().get(calendarId=cal_id, eventId=event_id).execute()
    event['colorId'] = color_id
    service.events().update(calendarId=cal_id, eventId=event_id,
                            body=event).execute()


def choose_calendar():
    # Print list of calendars and prompt user to choose one to work with
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
    # Return the id number of the chosen calendar
    return calendar_list['items'][choice]['id']


def read_config(filename):
    # Reads in config file and generates a dictionary
    #  mapping event names to specific colorIDs
    name_color_dict = {}
    with open(filename) as config:
        for line in config:
            config_record = line.rstrip("\n").split(",")
            name_color_dict[config_record[0]] = config_record[1]
    return name_color_dict

if __name__ == "__main__":
    main()