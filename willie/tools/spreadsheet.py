# coding=utf8
"""Functions for managing Google Sheets."""
from __future__ import unicode_literals
from __future__ import absolute_import
import gspread, json
from oauth2client.client import SignedJwtAssertionCredentials

def google_sheet_get(spreadsheet_name):
    json_key = json.load(open('cred.json'))
    scope = ['https://spreadsheets.google.com/feeds']
    email = json_key['client_email']
    key = json_key['private_key'].encode('utf-8')
    credentials = SignedJwtAssertionCredentials(email, key, scope)
    gc = gspread.authorize(credentials)
    return gc.open_by_key(spreadsheet_name)