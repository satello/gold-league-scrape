import os
import datetime

from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow, AccessTokenCredentials, Credentials
import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
# from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.service_account import ServiceAccountCredentials


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'goldleagueffball-994848912398.json'
APPLICATION_NAME = 'Gold League Sheet'
GOLD_LEAGUE_SHEET_ID = '1YDb26U8rCV0ISmumHt_oa1VIEcZvEhVeC8Z9B59JoIQ'
BIEBS_SHEET_ID = '1EA5qYoN-zeuiiyrLYYta7cGFX_zS0QFp1IpoWbozcJo'
MY_SHEET_TEMP = '1Fj1z0A3LmAamKtqTnAzMFc-fCbzJCDRCGR2Hn8wcOoc'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    # home_dir = os.path.dirname(os.path.abspath(__file__))
    # credential_path = os.path.join(home_dir, 'static/credentials.json')
    #
    # store = Storage(credential_path)
    # credentials = store.get()
    # if not credentials or credentials.invalid:
    #     flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    #     flow.user_agent = APPLICATION_NAME
    #     if flags:
    #         credentials = tools.run_flow(flow, store, flags)
    #     else: # Needed only for compatibility with Python 2.6
    #         credentials = tools.run(flow, store)
    #     print('Storing credentials to ' + credential_path)
    # return credentials
    #
    # return AppAssertionCredentials(
    # 'https://www.googleapis.com/auth/sqlservice.admin')
    # scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    # FOR LOCAL
    home_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../')

    credential_path = os.path.join(home_dir, CLIENT_SECRET_FILE)

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        credential_path, scopes=SCOPES)

    # FOR GAE
    # credentials = AppAssertionCredentials(SCOPES)

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

    # players
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
            player_dict = {
                "player_name": row[0],
                "price": row[1].strip('$'),
            }
            if len(row) >= 4:
                player_dict["years_remaining"] = row[3]
            else:
                player_dict["years_remaining"] = None
            players.append(player_dict)
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
                "name": row[0],
                "cap_room": row[1].strip('$'),
                "years_remaining": row[2],
                "spots_available": row[3]

            })
        return teams


def get_players_dynastyfftools_cloud_safe():
    """
    basic cloud infastructure doesn't allow Selenium binaries necessary. Use biebs sheet as fallback
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    rangeName = "DynastyFFTools!A2:H"
    result = service.spreadsheets().values().get(
        spreadsheetId=MY_SHEET_TEMP, range=rangeName).execute()
    player_rows = result.get('values', [])

    return player_rows
