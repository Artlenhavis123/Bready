from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.now().replace(day=1).isoformat() + 'Z'  # 'Z' indicates UTC time

        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        payrate = 10.55
        tot_hours = 0
        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            if event['summary'] == 'Work':
                start = convertDate(start)
                end = convertDate(end)

                shift_len = end - start
                seconds = shift_len.seconds
                hours = seconds//3600

                tot_hours = tot_hours + hours

                start = start.strftime('%d/%m/%Y %a %I:%M %p')
                end = end.strftime("%I:%M %p")

                print(f"{start} - {end}: {event['summary']}({shift_len})")


        print(f"Total Hours: {tot_hours}")
        pay = tot_hours * payrate
        pay = float("{0:.2f}".format(pay))
        print(f"Planned Pay: {pay}")

    except HttpError as error:
        print('An error occurred: %s' % error)


def convertDate(date):
    date = date.replace('+01:00',"")
    date = date.replace('T'," ")
    date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    return date


if __name__ == '__main__':
    main()