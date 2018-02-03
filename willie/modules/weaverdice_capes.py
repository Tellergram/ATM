# coding=utf8
"""
weaverdice_luck.py - Willie Dice Module
Copyright 2015, Teller
"""
from __future__ import unicode_literals
from willie.module import commands, example, priority, thread, interval, rule
from willie.tools.spreadsheet import google_sheet_get
from willie.tools.common import is_integer, say, mute_say, set_delay_timer, get_delay_timer
import random, re
import unicodedata

shared_var = {}
def setup(bot):
    shared_var['sheet'] = '1_syrsmptzWG0u3xdY3qzutYToY1t3I8s6yaryIpfckU'
    shared_var['re_delimiters'] = re.compile(r"[ /]+")
    shared_var['re_aka'] = re.compile(r"(?:AKA|also known as|previously known as) (['\"]?)(.*?)([\.'\"]( |$)|$)", re.MULTILINE)

    print 'Fetching capes...'
    cache_capes()
    cache_dibs()

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii
    
def cache_capes():
    spreadsheet = google_sheet_get(shared_var['sheet'])
    shared_var['capes'] = []
    
    #Canon capes
    worksheet = spreadsheet.worksheet('Canon')
    values = worksheet.get_all_values()
    
    for value in values[1:]:
        name = value[0].encode('utf-8', 'ignore').decode('utf-8').strip()
        alias = value[1].encode('utf-8', 'ignore').decode('utf-8').strip()
        if not name:
            name = alias
            alias = ''
            
        if name:
            cape = {
                'name': name,
                'alias': [alias],
                'power': value[2].encode('utf-8', 'ignore').decode('utf-8').strip(),
                'affiliation': value[3].encode('utf-8', 'ignore').decode('utf-8').strip(),
                'alignment': '',
                'classification': value[4].encode('utf-8', 'ignore').decode('utf-8').strip(),
                'character type': '',
                'campaign': 'Worm',
                'owner': 'Wildbow',
                'status': '',
                'notes': ''
            }
            cape['s_name'] = [cape['name'].lower(), remove_accents(cape['name']).lower()]
            cape['s_alias'] = [x.lower() for x in cape['alias']] + [remove_accents(x).lower() for x in cape['alias']]
            shared_var['capes'].append(cape)
            
    #Non-Canon capes
    worksheet = spreadsheet.worksheet('Non-Canon')
    values = worksheet.get_all_values()
    
    for value in values[1:]:
        name = value[0].encode('utf-8', 'ignore').decode('utf-8').strip()
        alias = value[1].encode('utf-8', 'ignore').decode('utf-8').strip()
        if not name:
            name = alias
            alias = ''
            
        if name:
            cape = {
                'name': name,
                'alias': [alias],
                'power': value[2].encode('utf-8', 'ignore').decode('utf-8').strip(),
                'affiliation': value[3].encode('utf-8', 'ignore').decode('utf-8').strip(),
                'alignment': value[4].encode('utf-8', 'ignore').decode('utf-8').strip(),
                'classification': value[5].encode('utf-8', 'ignore').decode('utf-8').strip(),
                'character type': value[6].encode('utf-8', 'ignore').decode('utf-8').strip(),
                'campaign': value[7].encode('utf-8', 'ignore').decode('utf-8').strip(),
                'owner': value[8].encode('utf-8', 'ignore').decode('utf-8').strip(),
                'status': value[9].encode('utf-8', 'ignore').decode('utf-8').strip(),
                'notes': value[10].encode('utf-8', 'ignore').decode('utf-8').strip()
            }
            
            for match in shared_var['re_aka'].findall(cape['notes']):
                cape['alias'].append(match[1])
                
            cape['s_name'] = [cape['name'].lower(), remove_accents(cape['name']).lower()]
            cape['s_alias'] = [x.lower() for x in cape['alias']] + [remove_accents(x).lower() for x in cape['alias']]
            shared_var['capes'].append(cape)
            
def cache_dibs():
    shared_var['dibs'] = []
    
    #Dibs
    spreadsheet = google_sheet_get(shared_var['sheet'])
    worksheet = spreadsheet.worksheet('Dibs')
    values = worksheet.get_all_values()
    
    for value in values[1:]:
        name = value[0].encode('utf-8', 'ignore').decode('utf-8').strip()
        owner = value[1].encode('utf-8', 'ignore').decode('utf-8').strip()
        shared_var['dibs'].append({
            'name': name,
            'owner': owner
        })

@example('$refresh [luck/cards/triggers/capes]')
@commands('refresh', 'cache')
@priority('low')
def refresh(bot, trigger):
    """Forces the cache to update."""
    if not trigger.group(2) or trigger.group(2).lower() == 'capes':
        cache_capes()
        say(bot,"Cape cache updated.")
        
    if not trigger.group(2) or trigger.group(2).lower() == 'dibs':
        cache_dibs()
        say(bot,"Dibs cache updated.")
                
@example('$cape Skitter')
@commands('cape')
@priority('low')
def cape(bot, trigger):
    """Searches the cape database for a name or ID."""

    ids = []
    if trigger.group(2):
        if is_integer(trigger.group(2)):
            ids = [(int(trigger.group(2)), 0)]
        elif trigger.group(2)[0] == '#' and is_integer(trigger.group(2)[1:]):
            ids = [(int(trigger.group(2)[1:]), 0)]
        else:
            key = trigger.group(2).lower()
            ids = []
            
            for id, cape in enumerate(shared_var['capes']):
                # PERFECT MATCH

                if any(key == alias for alias in cape['s_name']):
                    ids.append((id, 0))
                    continue
                    
                if any(key == alias for alias in cape['s_alias'][1:]):
                    ids.append((id, 1))
                    continue

                if key == cape['s_alias'][0]:
                    ids.append((id, 2))
                    continue
                    
                # SEMI-FUZZY MATCH 1
                
                if key in [words for segments in cape['s_name'] for words in segments.split()]:
                    ids.append((id, 3))
                    continue
                
                if key in [words for segments in cape['s_alias'][1:] for words in segments.split()]:
                    ids.append((id, 4))
                    continue

                if key in cape['s_alias'][0].split():
                    ids.append((id, 5))
                    continue                    
                    
                # SEMI-FUZZY MATCH 2
                
                if any(alias.startswith(key) for alias in cape['s_name']):
                    ids.append((id, 6))
                    continue
                    
                if any(alias.startswith(key) for alias in cape['s_alias'][1:]):
                    ids.append((id, 7))
                    continue

                if cape['s_alias'][0].startswith(key):
                    ids.append((id, 8))
                    continue
                    
                # FUZZY MATCH
                
                if any(key in alias for alias in cape['s_name']):
                    ids.append((id, 9))
                    continue
                    
                if any(key in alias for alias in cape['s_alias'][1:]):
                    ids.append((id, 10))
                    continue

                if key in cape['s_alias'][0]:
                    ids.append((id, 11))
                    continue                    
                    
    if ids:
        ids.sort(key=lambda tup: tup[1])
    
        #ID
        cape = shared_var['capes'][ids[0][0]]
        
        #NAME
        message = '[#' + str(ids[0][0]) + '] ' + cape['name']
        
        #ALIASES
        if [x for x in cape['alias'] if x]:
            message = message + ' (AKA ' + ', '.join([x for x in cape['alias'] if x]) + ')'
    
        #OWNER + NPC/PC
        message = message + ' is'
        if cape['owner']:
            if cape['owner'].endswith(('s', 'z')):
                message = message + ' ' + cape['owner'] + "' "
            else:
                message = message + ' ' + cape['owner'] + "'s "
            
            if cape['character type']:
                message = message + cape['character type']
            else:
                message = message + 'character'
        else:
            if cape['character type']:
                if cape['character type'].lower() == 'NPC' or cape['character type'].lower().startswith(('a', 'e', 'i', 'o', 'u')):
                    message = message + ' an ' + cape['character type']
                else:
                    message = message + ' a ' + cape['character type']
            else:
                message = message + ' a character'

        #CAMPAIGN
        if cape['campaign']:
            message = message + ' from ' + cape['campaign'] + '.'
        else:
            message = message + ' from an unknown campaign.'
        
        #EVERYTHING ELSE
        for key in ('alignment', 'status', 'affiliation', 'classification', 'power', 'notes'):
            if cape[key]:
                message = message + ' | ' + key.upper() + ': ' + cape[key]    
        
        #OUTPUT
        message = re.sub('(?i)wildbow', "'bow", message)
        say(bot, message)
        if len(ids) > 1:
            say(bot, 'See also: ' + ', '.join(shared_var['capes'][id[0]]['name'] + ' [#' + str(id[0]) + ']' for id in ids[1:10]))
        
        return 
    else:
        return say(bot, 'No cape found.')
        
@example('$dibs Skitter')
@commands('dibs')
@priority('low')
@thread(False)
def dibs(bot, trigger):
    """Claims a cape name. To see all of the cape names you've claimed, use '$dibs'"""
    
    if trigger.group(2):
        name = trigger.group(2).strip()
        
        say(bot, 'Calling dibs. This might take a moment...')
        
        # Update the dibs cache
        cache_dibs()
        
        # Make sure the name is not already claimed
        cape = next((item for item in shared_var['dibs'] if item['name'].upper() == name.upper()), None)
        
        if cape:
            if cape['owner'].upper() == trigger.nick.upper():
                return say(bot, 'You already called dibs on that name.')
            else:
                return say(bot, cape['owner'] + ' already called dibs on that name.')
                
        # Add it to the spreadsheet
        owner = trigger.nick
        spreadsheet = google_sheet_get(shared_var['sheet'])
        worksheet = spreadsheet.worksheet('Dibs')
        
        # Try to find a blank row
        slot = None
        for index, cape in enumerate(shared_var['dibs']):
            if cape['name'] == '':
                slot = index
                break
                
        # Update worksheet and cache
        if slot is not None:
            worksheet.update_cell(slot + 2, 1, name)
            worksheet.update_cell(slot + 2, 2, owner)
            shared_var['dibs'][index]['name'] = name
            shared_var['dibs'][index]['owner'] = owner
        else:
            worksheet.append_row([name,owner])
        
            # Add it to the cache
            shared_var['dibs'].append({
                'name': name,
                'owner': owner
            })
        
        return say(bot, 'Done!')
    else:
        # Show all capes with dibs
        capes = [cape['name'] for cape in shared_var['dibs'] if cape['owner'].upper() == trigger.nick.upper()]
        if len(capes) == 0:
            return say(bot, 'Your have no capes.')
        else:
            return say(bot, 'Your capes are: ' + ', '.join(capes))
            
@example('$undibs Skitter')
@commands('undibs')
@priority('low')
@thread(False)
def undibs(bot, trigger):
    """Reverse a claim on a cape name."""
    
    if trigger.group(2):
        name = trigger.group(2)
        say(bot, 'Removing dibs. This might take a moment...')
        # Update the dibs cache
        cache_dibs()
    
        # Check for a cape with the correct details
        for id, cape in enumerate(shared_var['dibs']):
            if cape['name'].upper() == name.upper() and cape['owner'].upper() == trigger.nick.upper():
                # Remove cape
                spreadsheet = google_sheet_get(shared_var['sheet'])
                worksheet = spreadsheet.worksheet('Dibs')
                worksheet.update_cell(id + 2, 1, '')
                worksheet.update_cell(id + 2, 2, '')
                return say(bot, 'Dibs removed.')
        return say(bot, "You don't have dibs on that name.")
    else:
        return say(bot, 'Please specify a cape.')
    