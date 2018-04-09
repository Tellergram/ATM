# coding=utf8
"""
weaverdice_main.py - Willie Dice Module
Copyright 2015, Teller
"""
from __future__ import unicode_literals
from willie.module import commands, example, priority, thread, interval, rule
from willie.tools.spreadsheet import google_sheet_get
from willie.tools.common import is_integer, is_float, mute_say, say, set_delay_timer, get_delay_timer
import random, re, markovgen

shared_var = {}

def setup(bot):
    shared_var['re_claim'] = re.compile(r"^([0-9]+) ?([^\[]+)? ?(\[.*\])? ?([^\]]+)?$")
    shared_var['trigger_sheet'] = '1mABmj3VVT-KyDpF8Xn67-HKQraCNK_qb6z5HCRUMdwk'
    
    set_delay_timer('trigger', 0)
    set_delay_timer('claim', 0)
    set_delay_timer(['mover', 'shaker', 'brute', 'breaker', 'master', 'tinker', 'blaster', 'thinker', 'striker', 'changer', 'trump', 'stranger'], 0)
    for i in ['mover', 'shaker', 'brute', 'breaker', 'master', 'tinker', 'blaster', 'thinker', 'striker', 'changer', 'trump', 'stranger']:
        shared_var['increment::' + i] = 0

    print('Fetching triggers...')
    cache_triggers()
    
@interval(60*5)
def cache_triggers(bot = None):
    spreadsheet = google_sheet_get(shared_var['trigger_sheet'])
    
    #classes
    worksheet = spreadsheet.worksheet('Count & Frontpage')
    values = worksheet.col_values(2)
    shared_var['classes'] = values[6:18]
    
    #triggers
    worksheet = spreadsheet.worksheet('Triggers')
    values = worksheet.col_values(1)
    shared_var['trigger_list'] = []
    for i, v in enumerate(values):
        if not v:
            shared_var['trigger_list'].append({
                'prefix': '',
                'text': 'Blank.',
                'blank': True
            })
        elif v != "100 Triggers at Maximum, please.":
            shared_var['trigger_list'].append({
                'prefix': '['+str(i+1)+']: ',
                'text': v.encode('utf-8', 'ignore').decode('utf-8'),
                'blank': False
            })
    
    #used
    worksheet = spreadsheet.worksheet('Used')
    values = worksheet.col_values(2)
    shared_var['used_list'] = []
    for i, v in enumerate(values[1:]):
        if not v:
            shared_var['used_list'].append({
                'prefix': '',
                'text': 'Blank.',
                'blank': True
            })
        else:
            shared_var['used_list'].append({
                'prefix': '{'+str(i+2)+'}: ',
                'text': v.encode('utf-8', 'ignore').decode('utf-8'),
                'blank': False
            })

def update_trigger_cache(rows):
    shared_var['trigger_list']=[]
    for i, v in enumerate(rows):
        if not v:
            shared_var['trigger_list'].append({
                'prefix': '',
                'text': 'Blank.',
                'blank': True
            })
        else:
            shared_var['trigger_list'].append({
                'prefix': '['+str(i+1)+']: ',
                'text': v.encode('utf-8', 'ignore').decode('utf-8'),
                'blank': False
            })
            
def update_used_cache(rows):
    shared_var['used_list']=[]
    for i, v in enumerate(rows):
        if not v:
            shared_var['used_list'].append({
                'prefix': '',
                'text': '',
                'blank': True
            })
        else:
            shared_var['used_list'].append({
                'prefix': '{'+str(i+2)+'}: ',
                'text': v.encode('utf-8', 'ignore').decode('utf-8'),
                'blank': False
            })
            
@example('$refresh [luck/cards/triggers/capes]')
@commands('refresh', 'cache')
@priority('low')
def refresh(bot, trigger):
    """Forces the cache to update."""
    if not trigger.group(2) or trigger.group(2).lower() == 'triggers':
        cache_triggers()
        return say(bot,"Trigger cache updated.")
    
@example('$trigger')
@example('$trigger 42')
@commands('trigger')
@commands('bligelwer')
@priority('low')
def trigger(bot, trigger):
    """Fetches a trigger from the Weaver Dice trigger spreadsheet."""
    
    #Use the provided trigger if there is one
    if trigger.group(2):
        #Make sure the trigger number a valid integer
        if not is_integer(trigger.group(2)):
            return say(bot, "Please provide a valid trigger number.")        
        
        #Make sure the trigger number is in range
        trigger_index = int(trigger.group(2))
        if trigger_index > len(shared_var['trigger_list']) or trigger_index == 0:
            return say(bot, "Trigger '" + str(trigger_index) + "' is out of range.")

        t = shared_var['trigger_list'][trigger_index-1]
        return mute_say(bot, trigger, trigger.nick + ' ' + t['prefix'] + t['text'], 6)
    else:
        if trigger.is_privmsg is False:
            delay = get_delay_timer('trigger')
            if delay > 0:
                return say(bot, "ZzZz...["+str(delay)+"s]")
            set_delay_timer('trigger', 30)
    
        t = random.choice([x for x in shared_var['trigger_list'] if x['blank'] == False])
        return mute_say(bot, trigger, trigger.nick + ' ' + t['prefix'] + t['text'], 6)
        
@example('$used')
@example('$used 42')
@commands('used')
@priority('low')
def used(bot, trigger):
    """Fetches a used trigger from the Weaver Dice trigger spreadsheet."""
    
    #Use the provided trigger if there is one
    if trigger.group(2):
        #Make sure the trigger number a valid integer
        if not is_integer(trigger.group(2)):
            return say(bot,"Please provide a valid trigger number.")        
        
        #Make sure the trigger number is in range
        trigger_index = int(trigger.group(2))
        if trigger_index>len(shared_var['used_list'])+1 or trigger_index < 2:
            return say(bot,"Used trigger '"+str(trigger_index)+"' is out of range.")

        t = shared_var['used_list'][trigger_index-2]
        return mute_say(bot, trigger, trigger.nick + ' ' + t['prefix'] + t['text'], 6)
    else:
        if trigger.is_privmsg is False:
            delay=get_delay_timer('trigger')
            if delay>0:
                return say(bot,"ZzZz...["+str(delay)+"s]")
            set_delay_timer('trigger',30)
    
        t = random.choice([x for x in shared_var['used_list'] if x['blank'] == False])
        return mute_say(bot, trigger, trigger.nick + ' ' + t['prefix'] + t['text'], 6)

@example('$claim 42 Campaign Name [Player_Name] Short description of the power.')
@commands('claim')
@priority('low')
@thread(False)
def claim(bot, trigger):
    """Moves a trigger to the used section of the Weaver Dice trigger spreadsheet.
    The square brackets around Player_Name should be included."""
    
    if trigger.sender.lower() != '#weaverdice':
        return say(bot,'Please perform claims in #Weaverdice.')
    
    #Validate command
    if not trigger.group(2):
        return say(bot,"Specify a trigger from 1-100.")
        
    data = shared_var['re_claim'].match(trigger.group(2))
        
    if data.group(1):
        if is_integer(data.group(1)):
            trigger_index = int(data.group(1))
        else:
            return say(bot,"Invalid trigger index.")
    else:
        return say(bot,"Specify a trigger from 1-100.")
    
    game = data.group(2).strip() if data.group(2) else '?'
    claimer = data.group(3).strip()[1:-1] if data.group(3) else trigger.nick
    description = data.group(4).strip() if data.group(4) else ''
    
    delay=get_delay_timer('claim')
    if delay>0:
        return say(bot,"ZzZz...["+str(delay)+"s]")
    set_delay_timer('claim',15)
        
    #Initialize spreadsheet
    spreadsheet = google_sheet_get(shared_var['trigger_sheet'])
    trigger_worksheet = spreadsheet.worksheet('Triggers')
    trigger_worksheet_height = trigger_worksheet.row_count
    used_worksheet = spreadsheet.worksheet('Used')
    used_worksheet_height = used_worksheet.row_count
    say(bot,'Claiming trigger. This might take a moment...')
    
    #Sort through trigger list and fetch the trigger string/author. Might as well grab the whole thing so the trigger cache can be updated.
    triggers = [["",""] for y in range(trigger_worksheet_height)]
    cell_list = trigger_worksheet.range('A1:B'+str(trigger_worksheet_height))
    for cell in cell_list:
        triggers[cell.row-1][cell.col-1] = cell.value
    
    trigger_string = triggers[trigger_index-1][0]
    if not trigger_string:
        return say(bot,"...Trigger '"+str(trigger_index)+"' is blank.")
    trigger_string=trigger_string.encode('utf-8', 'ignore').decode('utf-8')
    
    trigger_author = triggers[trigger_index-1][1]
    if not trigger_author:
        trigger_author="?"
    else:
        trigger_author=trigger_author.encode('utf-8', 'ignore').decode('utf-8')
    
    #Sort through used trigger list and find blank spot. Grab the whole thing so the cache can be updated.
    used_triggers = used_worksheet.col_values(2)
    used_triggers += [None] * (used_worksheet_height - len(used_triggers))
    update_used_cache(used_triggers[1:])
    
    #Find blank spot to append used trigger. If none is available, append a row.
    try:
        slot = used_triggers[1:].index(None)+2
        used_worksheet.update_cell(slot, 1, game)
        used_worksheet.update_cell(slot, 2, trigger_string)
        used_worksheet.update_cell(slot, 3, trigger_author)
        used_worksheet.update_cell(slot, 4, claimer)
        used_worksheet.update_cell(slot, 5, description)
        shared_var['used_list'][slot-2] = {
            'prefix': '{'+str(slot)+'}: ',
            'text': trigger_string.encode('utf-8', 'ignore').decode('utf-8'),
            'blank': False
        }
    except ValueError:
        used_worksheet.append_row([game,trigger_string,trigger_author,claimer,description])
        shared_var['used_list'].append({
            'prefix': '{'+str(used_worksheet_height+1)+'}: ',
            'text': trigger_string.encode('utf-8', 'ignore').decode('utf-8'),
            'blank': False
        })
        slot = used_worksheet_height+1
    
    #Update trigger list
    triggers.pop(trigger_index-1)
    triggers.append([""]*2)
    for cell in cell_list:
        cell.value = triggers[cell.row-1][cell.col-1]
        if not cell.value:
            cell.value=""

    trigger_worksheet.update_cells(cell_list)
    
    #Update trigger cache
    update_trigger_cache([row[0] for row in triggers])
    
    #Fin
    return say(bot,'...Trigger ['+str(trigger_index)+'] moved to Used Trigger slot {'+str(slot)+'}.')
    
@example('$unclaim 42')
@commands('unclaim')
@priority('low')
@thread(False)
def unclaim(bot, trigger):
    """Reverses a claim on a trigger, moving it back to the Weaver Dice trigger spreadsheet."""
    
    if trigger.sender.lower() != '#weaverdice':
        return say(bot,'Please perform unclaims in #Weaverdice.')
    
    #Validate command
    if not trigger.group(2):
        return say(bot,"Specify a used trigger from 2+.")
    trigger_index = int(trigger.group(2))
    if (trigger_index<2):
        return say(bot,"Specify a used trigger from 2+.")

    delay=get_delay_timer('claim')
    if delay>0:
        return say(bot,"ZzZz...["+str(delay)+"s]")
    set_delay_timer('claim',15)
        
    #Initialize spreadsheet
    spreadsheet = google_sheet_get(shared_var['trigger_sheet'])
    worksheet2 = spreadsheet.worksheet('Used')
    h = worksheet2.row_count
    
    #Sort through used trigger list and fetch string/author. Grab the whole thing so the cache can be updated.
    used_triggers = [["","","","",""] for y in range(h)]
    cell_list = worksheet2.range('A1:E'+str(h))
    for cell in cell_list:
        used_triggers[cell.row-1][cell.col-1] = cell.value
    
    trigger_string = used_triggers[trigger_index-1][1]
    
    if not trigger_string:
        return say(bot,"Used trigger '"+str(trigger_index)+"' is blank.")
    if used_triggers[trigger_index-1][2]:
        trigger_author = used_triggers[trigger_index-1][2]
    else:
        trigger_author = "?"
    trigger_string = trigger_string.encode('utf-8', 'ignore').decode('utf-8')
    trigger_author = trigger_author.encode('utf-8', 'ignore').decode('utf-8')
    say(bot,'Unclaiming trigger. This might take a moment...')

    #Fetch trigger list and find an empty slot to insert this trigger in. Update cache while we're at it.
    worksheet = spreadsheet.worksheet('Triggers')
    worksheet_height = worksheet.row_count
    triggers = worksheet.col_values(1)
    triggers += [None] * (worksheet_height - len(triggers))
    update_trigger_cache(triggers)

    # Find the empty slot
    slot = None
    for i, dic in enumerate(shared_var['trigger_list']):
        if dic['blank']:
            slot = i + 1
            break

    if slot is None:
        return say(bot,"...The trigger list is full.")
    
    #Update trigger list + cache
    worksheet.update_cell(slot, 1, trigger_string)
    worksheet.update_cell(slot, 2, trigger_author)
    shared_var['trigger_list'][slot-1] = {
        'prefix': '['+str(slot)+']: ',
        'text': trigger_string,
        'blank': False
    }
        
    #Remove used trigger from trigger list
    used_triggers.pop(trigger_index-1)
    used_triggers.append([""]*5)
    h = len(used_triggers)
    for cell in cell_list:
        cell.value = used_triggers[cell.row-1][cell.col-1]
        
    worksheet2.update_cells(cell_list)
    
    #Update trigger cache
    used_triggers.pop()
    update_used_cache([row[1] for row in used_triggers[1:]])

    return say(bot,'...Used Trigger {'+str(trigger_index)+'} moved to Trigger slot ['+str(slot)+'].')
        

@example('$classifications')
@commands('classifications')
@commands('classes')
@priority('low')
def classifications(bot, trigger):
    """Returns the current classification counts."""
    string = ''
    for i, v in enumerate(['Mover', 'Shaker', 'Brute', 'Breaker', 'Master', 'Tinker', 'Blaster', 'Thinker', 'Striker', 'Changer', 'Trump', 'Stranger']):
        string = string + ' | ' + v + ': ' + shared_var['classes'][i]
    return say(bot, string[3:])

@example('$mover -1')
@commands('mover')
@commands('shaker')
@commands('brute')
@commands('breaker')
@commands('master')
@commands('tinker')
@commands('blaster')
@commands('thinker')
@commands('striker')
@commands('changer')
@commands('trump')
@commands('stranger')
@priority('low')
def classification(bot, trigger):
    """Increments the specified classification by the provided number."""

    if trigger.sender.lower() != '#weaverdice':
        return say(bot,'Please perform increments in #Weaverdice.')
    
    if trigger.group(2):
        if trigger.group(1).lower()=="thinker" and trigger.group(2).lower()=="run":
            return say(bot,'"Thinker. Don\'t worry about the number. Just run."')
        try:
            increment = float(trigger.group(2))
        except ValueError:
            return say(bot,"Invalid increment.")
        except AttributeError:
            return say(bot,"Invalid input.")
        if (increment==0):
            return say(bot,"Nope, not wasting my time incrementing by 0.")
    else:
        return say(bot,"Specify a number to increment "+trigger.group(1).lower()+" by. If you're trying to generate an npc, the command is '$npc "+trigger.group(1).lower()+"'")
    type = trigger.group(1).lower()
    
    delay=get_delay_timer(type)
    if delay>0 and increment*-1!=shared_var['increment::'+type]:
        return say(bot,"ZzZz...["+str(delay)+"s]")
    set_delay_timer(type,15)
    shared_var['increment::'+type]=increment
    
    #classes
    spreadsheet = google_sheet_get(shared_var['trigger_sheet'])
    worksheet = spreadsheet.worksheet('Count & Frontpage')
    values = worksheet.col_values(2)
    shared_var['classes'] = values[6:18]
    cell = ['mover','shaker','brute','breaker','master','tinker','blaster','thinker','striker','changer','trump','stranger'].index(type)
    try:
        shared_var['classes'][cell] = ('%f' % (float(shared_var['classes'][cell])+increment)).rstrip('0').rstrip('.')
    except:
        return say(bot,"Invalid count for '"+type.title()+"'.")
    
    worksheet.update_cell(7+cell, 2, shared_var['classes'][cell])
    return say(bot,type.title()+" count modified by "+str(increment)+". Current value: "+shared_var['classes'][cell])

@example('$markov [chain size] [length]')
@commands('markov')
@priority('low')
def markov(bot, trigger):
    """Returns a markov chain composed of words from current and used triggers."""

    chain = 3
    size = 42
    if trigger.group(2):
        data = trigger.group(2).split()
        try:
            chain = int(data[0])
        except ValueError:
            return say(bot,"Invalid markov chain length .")
        except AttributeError:
            return say(bot,"Invalid input.")
        if (chain==0):
            return say(bot,"...")
        if (chain>10 or chain<2):
            return say(bot,"Please specify a chain length from 2 to 10.")
            
        if len(data)>1:
            try:
                size = int(data[1])
            except ValueError:
                return say(bot,"Invalid markov size.")
            except AttributeError:
                return say(bot,"Invalid input.")
            if (size<1 or size>200):
                return say(bot,"Please specify a markov size from 1 to 200.")
    words = []
    for input in shared_var['used_list']:
        if not input['blank']:
            words.append(input['text'])
            
    for input in shared_var['trigger_list']:
        if not input['blank']:
            words.append(input['text'])
    markov = markovgen.Markov(words,chain)
    text = markov.generate_markov_text(size)
    text = text[:1].upper() + text[1:]
    if text[-1] not in ['.','!','?']:
        if text[-1] in [',',':',';']:
            text = text[:-1]+'.'
        else:
            text = text + '.'
            
    if (size == 4):
        text = '"'+text[:-1]+'," Scion whispered.'
    return say(bot,text,3)

@example('$simurgh [adjustment] [player]')
@commands('simurgh')
@commands('imurgh')
@priority('low')
def simurgh(bot, trigger):
    if trigger.nick.lower() not in ['wildbow','wildbow|gm','wild|gm','teller','teller|gm']:
        return 1

    tag = ''
    if trigger.group(2):
        #adjustment
        data = trigger.group(2).split(' ',1)
        try:
            offset = min(int(data[0]),90)
        except ValueError:
            return say(bot,"Invalid adjustment.")
        except AttributeError:
            return say(bot,"Invalid adjustment.")
        #tag
        if len(data)>1:
            tag = data[1]
    else:
        offset = random.randrange(0,90)
    percentage = offset+random.randrange(0,101-offset)
    if not tag:
        return say(bot,"Adjusted: ("+str(percentage)+"%)")
    else:
        return say(bot,"Adjusted '"+tag+"': ("+str(percentage)+"%)")