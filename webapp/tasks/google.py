import os
import datetime

from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow, AccessTokenCredentials, Credentials
import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gold League Sheet'
GOLD_LEAGUE_SHEET_ID = '1YDb26U8rCV0ISmumHt_oa1VIEcZvEhVeC8Z9B59JoIQ'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_player_information_for_team(sheet_owner_name):
    """Gets all the player information for an owner from google sheet

    @params:
    sheet_owner_name: <string> e.g. Sam, Zach, Tim etc.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    rangeName = '%s!B2:E' % sheet_owner_name
    result = service.spreadsheets().values().get(
        spreadsheetId=GOLD_LEAGUE_SHEET_ID, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        raise RuntimeError('No player data found for %s') % sheet_owner_name
    else:
        players = []
        for row in values:
            if row[0] == "Open":
                continue
            # row = name, price, expiration year, years remaining
            players.append({
                "player_name": row[0],
                "price": row[1].strip('$'),
                "years_remaining": row[3]

            })
        return players

def get_team_information():
    """
    Gets all the team information for the league
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    rangeName = "'Team Info'!B3:E"
    result = service.spreadsheets().values().get(
        spreadsheetId=GOLD_LEAGUE_SHEET_ID, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        raise RuntimeError('No team data found')
    else:
        teams = []
        for row in values:
            # row = name, price, expiration year, years remaining
            teams.append({
                "team_name": row[0],
                "cap_room": row[1].strip('$'),
                "years_remaining": row[2],
                "spots_available": row[3]

            })
        return teams
