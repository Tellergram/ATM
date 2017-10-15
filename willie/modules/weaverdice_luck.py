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

shared_var = {}
def setup(bot):
    shared_var['sheet'] = '1aHyZ7c7TIgt903mPinOakrgli2WZu5IRtiGYPCnCqDE'
    shared_var['re_delimiters'] = re.compile(r"[ /]+")
    set_delay_timer('luck', 0)
    print 'Fetching luck...'
    cache_luck()
        
def cache_luck():
    spreadsheet = google_sheet_get(shared_var['sheet'])
    worksheet = spreadsheet.worksheet('LUCK')
    values = worksheet.get_all_values()
    shared_var['luck_list'] = {"Life Perk":[],"Power Perk":[],"Life Flaw":[],"Power Flaw":[]}
    
    keys = ["Life Perk","Power Perk","Life Flaw","Power Flaw"]
    for j in range(2,6):
        key = keys[j-2]
        for i in range(1,79):
            if values[i][j].encode('utf-8', 'ignore').decode('utf-8').strip():
                text = values[i][j].encode('utf-8', 'ignore').decode('utf-8')
                keyword = text.split('.', 1)[0].lower().strip()

                shared_var['luck_list'][key].append({
                    'text': '['+key+' '+str(i+1)+']: '+text,
                    'keyword': keyword,
                    'blank': False
                })
            else:
                shared_var['luck_list'][key].append({
                    'text': '['+key+' '+str(i+1)+']: Blank',
                    'keyword': '',
                    'blank': True
                })

@example('$refresh [luck/cards/triggers/capes]')
@commands('refresh', 'cache')
@priority('low')
def refresh(bot, trigger):
    """Forces the cache to update."""
    if not trigger.group(2) or trigger.group(2).lower() == 'luck':
        cache_luck()
        return say(bot,"Luck cache updated.")
                
@example('$luck 6')
@commands('luck')
@priority('low')
def luck(bot,trigger):
    """Rolls 2dx (default 1d4, 1d4) and fetches the relevant perks and/or flaws from the detail sheet."""
    
    die = [4,4]
    if trigger.group(2):
        if is_integer(trigger.group(2)):
            sides = int(trigger.group(2))
            die = [4,sides]
        else:
            return luck_keyword(bot,trigger)
        if (sides<4):
            return say(bot,"The dice must have at least 4 sides.")
    
    delay = get_delay_timer('luck')
    if delay > 0:
        return say(bot,"ZzZz...["+str(delay)+"s]")
    set_delay_timer('luck',15)
    
    result = []
    roll = []
    for x in range(0,2):
        selection = ['None']*die[x]
        selection[0] = 'Life Flaw'
        selection[1] = 'Power Flaw'
        selection[die[x]-2] = 'Life Perk'
        selection[die[x]-1] = 'Power Perk'
        r = random.randint(1,die[x])
        roll.append(str(r)+"/"+str(die[x]))
        if selection[r-1] is not 'None':
            selection = random.choice([x for x in shared_var['luck_list'][selection[r-1]] if x['blank'] == False])['text']
            result.append(selection)
            
    roll_string = '['+', '.join(roll)+']'
    if result:
        result[0] = trigger.nick + ' ' + roll_string + ' ' + result[0]
        mute_say(bot, trigger, result, 20)
    else:
        return say(bot,trigger.nick + ' ' + roll_string + ' [None]')

def luck_keyword(bot, trigger, keyword=None, filter=None):
    if not keyword:
        keyword = trigger.group(2).lower()
    keys = shared_var['re_delimiters'].split(keyword)
    
    #Search For Exact Keyword
    response = None
    if not response and filter in [None, 'Life', 'Perk', 'Life Perk']:
        response = next((x for x in shared_var['luck_list']['Life Perk'] if x['keyword'] == keyword), None)
    if not response and filter in [None, 'Power', 'Perk', 'Power Perk']:
        response = next((x for x in shared_var['luck_list']['Power Perk'] if x['keyword'] == keyword), None)
    if not response and filter in [None, 'Life', 'Flaw', 'Life Flaw']:
        response = next((x for x in shared_var['luck_list']['Life Flaw'] if x['keyword'] == keyword), None)
    if not response and filter in [None, 'Power', 'Flaw', 'Power Flaw']:
        response = next((x for x in shared_var['luck_list']['Power Flaw'] if x['keyword'] == keyword), None)
    
    #Search For Partial Keyword
    if not response and filter in [None, 'Life', 'Perk', 'Life Perk']:
        response = next((x for x in shared_var['luck_list']['Life Perk'] if any(key in x['keyword'] for key in keys)), None)
    if not response and filter in [None, 'Power', 'Perk', 'Power Perk']:
        response = next((x for x in shared_var['luck_list']['Power Perk'] if any(key in x['keyword'] for key in keys)), None)
    if not response and filter in [None, 'Life', 'Flaw', 'Life Flaw']:
        response = next((x for x in shared_var['luck_list']['Life Flaw'] if any(key in x['keyword'] for key in keys)), None)
    if not response and filter in [None, 'Power', 'Flaw', 'Power Flaw']:
        response = next((x for x in shared_var['luck_list']['Power Flaw'] if any(key in x['keyword'] for key in keys)), None) 
    
    if not response:
        if not filter:
            return say(bot,"Invalid luck keyword.")
        else:
            return say(bot,"Invalid "+filter+" keyword.")
    else:
        return mute_say(bot, trigger, trigger.nick + ' ' + response['text'], 8)
    
@example('$life perk 8')
@commands('power')
@commands('life')
@commands('perk')
@commands('flaw')
@commands('advantage')
@commands('disadvantage')
@priority('low')
def luck_specific(bot,trigger):
    """Returns a power/life perk or flaw."""
    options = ['life perk', 'life flaw', 'life advantage', 'life disadvantage', 'power perk', 'power flaw', 'power advantage', 'power disadvantage','perk life', 'perk power', 'advantage life', 'advantage power', 'flaw life', 'flaw power', 'disadvantage life', 'disadvantage power', 'life', 'power', 'perk', 'flaw', 'advantage', 'disadvantage']
    string = trigger.group(1).lower()
    
    if trigger.group(2):
        string = string + ' ' + trigger.group(2).lower()
    
    for i in range(0,len(options)):
        if string.startswith(options[i]):
            option = options[i]
            break

    string = string[len(option):].strip()
    
    option = option.replace('disadvantage', 'flaw')
    option = option.replace('advantage', 'perk')
    option = option.title()
    
    if option.startswith("Perk") or option.startswith("Flaw"):
        option = ' '.join(reversed(option.split()))
    
    if string:
        if is_integer(string):
            if option in ['Life Perk', 'Life Flaw', 'Power Perk', 'Power Flaw']:
                data = int(string)
                if data>1 and data<80:
                    return say(bot,trigger.nick+' '+shared_var['luck_list'][option][data-2]['text'],8)
                else:
                    return say(bot,'Please provide a number 2 - 79.',3)
            else:
                return say(bot,'Please be more specific.',3)
        else:
            return luck_keyword(bot,trigger,string,option)
    else:
        if option == 'Perk':
            option = random.choice(['Life Perk','Power Perk'])
        elif option == 'Flaw':
            option = random.choice(['Life Flaw','Power Flaw'])
        elif option == 'Life':
            option = random.choice(['Life Perk','Life Flaw'])
        elif option == 'Power':
            option = random.choice(['Power Perk','Power Flaw'])
        selection = random.choice([x for x in shared_var['luck_list'][option] if x['blank'] == False])['text']
        return mute_say(bot, trigger, trigger.nick + ' ' + selection, 8)