# coding=utf8
"""
weaverdice_cards.py - Willie Dice Module
Copyright 2015, Teller
"""
from __future__ import unicode_literals
from willie.module import commands, example, priority, thread, interval, rule
from willie.tools.spreadsheet import google_sheet_get
from willie.tools.common import is_integer, is_float, say
from willie.tools.language import indefinite_article
import random, re

shared_var = {}
def setup(bot):
    shared_var['sheet'] = '1uBhJzlsWdm5Hl6ENoGHSzH-9xBio-BQqZyacNwPS-T0'
    shared_var['re_delimiters'] = re.compile(r"[ /]+")
    shared_var['re_cards'] = re.compile(r"\[([^\]]*)\]")
    shared_var['re_inline_cards'] = re.compile(r"{([^}\d\!][^}]*)}")
    shared_var['re_card_names'] = re.compile(r"\(\"(.*)\"\)")
    shared_var['re_card_odds'] = re.compile(r"\(\((.*)\)\)")
    shared_var['re_card_help'] = re.compile(r"\(\"\"(.*)\"\"\)")
    shared_var['re_card_an'] = re.compile(r"(a\(n\)) (\w+)")

    print 'Fetching cards...'
    cache_cards(bot)
        
def cache_cards(bot):
    bot.memory['card_help'] = {}
    shared_var['cards'] = {}
    shared_var['cards_by_keyword'] = {}
    shared_var['cards_by_group'] = {}
    shared_var['cards_by_name'] = {}
    
    shared_var['card_commands'] = []
    shared_var['card_sub_commands'] = []
    
    spreadsheet = google_sheet_get(shared_var['sheet'])
    worksheets = spreadsheet.worksheets()
    id = 0
    
    for worksheet in worksheets:
        values = worksheet.get_all_values()
        key_group = worksheet.title.lower()
        key_group = '' if key_group == 'main' else key_group + ' '
            
        for row in values:
            key_deck = row[0].lower()
            if key_group== '' and key_deck != 'commands':
                shared_var['card_sub_commands'].append(key_deck)

            for col in row[1:]:
                if col.strip():
                    help = ''
                    tmp_card = {
                        'text': col,
                        'cards': [],
                        'names': [],
                        'inline_cards': [],
                        'odds': 1
                    }
                
                    #Inline Cards
                    match = shared_var['re_inline_cards'].search(tmp_card['text'])
                    number = 1
                    while match and number<50:
                        tmp_card['inline_cards'].append([x.strip() for x in match.group(1).split('|')])
                        tmp_card['text'] = tmp_card['text'][:match.start(1)] + str(number) + tmp_card['text'][match.end(1):]
                        match = shared_var['re_inline_cards'].search(tmp_card['text'])
                        number = number + 1
                    
                    #Sub Cards
                    match = shared_var['re_cards'].search(tmp_card['text'])
                    number = 0
                    while match and number<50:
                        sub_card_data = match.group(1).split('|')
                        sub_card_data += [''] * (3 - len(sub_card_data))
                        subcard = {
                            'keyword': [],
                            'preface': [],
                            'tags': []
                        }
                        
                        if sub_card_data[0].strip():
                            subcard['keyword'] = [x.strip() for x in sub_card_data[0].split(',')]
                        
                        if sub_card_data[1].strip():
                            subcard['preface'] = [x.strip() for x in sub_card_data[1].split(',')]
                            
                        if sub_card_data[2].strip():
                            subcard['tags'] = [x.strip() for x in sub_card_data[2].split(',')]
                            
                        tmp_card['cards'].append(subcard)
                        
                        tmp_card['text'] = tmp_card['text'][:match.start()] + tmp_card['text'][match.end():]
                        match = shared_var['re_cards'].search(tmp_card['text'])
                        number = number + 1
                    
                    #Help
                    match = shared_var['re_card_help'].search(tmp_card['text'])
                    if match:
                        help = match.group(1).strip()
                        tmp_card['text'] = tmp_card['text'][:match.start()] + tmp_card['text'][match.end():]
                    
                    #Names
                    match = shared_var['re_card_names'].search(tmp_card['text'])
                    number = 0
                    while match and number<50:
                        tmp_card['names'].append(match.group(1).strip().lower())
                        tmp_card['text'] = tmp_card['text'][:match.start()] + tmp_card['text'][match.end():]
                        match = shared_var['re_card_names'].search(tmp_card['text'])
                        number = number + 1
                        
                    #Odds
                    match = shared_var['re_card_odds'].search(tmp_card['text'])
                    number = 0
                    while match and number<50:
                        if is_integer(match.group(1).strip().lower()):
                            tmp_card['odds'] = int(match.group(1).strip().lower())
                        tmp_card['text'] = tmp_card['text'][:match.start()] + tmp_card['text'][match.end():]
                        match = shared_var['re_card_odds'].search(tmp_card['text'])
                        number = number + 1
                    
                    tmp_card['text'] = tmp_card['text'].strip()
                    
                    tmp_card['id'] = id
                    id = id +1
                
                    #Group + Keyword
                    if key_group+key_deck in shared_var['cards']:
                        shared_var['cards'][key_group+key_deck].append(tmp_card)
                    else:
                        shared_var['cards'][key_group+key_deck] = [tmp_card]
                        
                    #Keyword
                    if key_deck in shared_var['cards_by_keyword']:
                        shared_var['cards_by_keyword'][key_deck].append(tmp_card)
                    else:
                        shared_var['cards_by_keyword'][key_deck] = [tmp_card]
                        
                    #Group
                    if key_group.strip() in shared_var['cards_by_group']:
                        shared_var['cards_by_group'][key_group.strip()].append(tmp_card)
                    else:
                        shared_var['cards_by_group'][key_group.strip()] = [tmp_card]
                        
                    #Name
                    for name in tmp_card['names']:
                        if key_group+key_deck+' '+name in shared_var['cards_by_name']:
                            shared_var['cards_by_name'][key_group+key_deck+' '+name].append(tmp_card)
                        else:
                            shared_var['cards_by_name'][key_group+key_deck+' '+name] = [tmp_card]

                    #Commands
                    if key_group+key_deck == 'commands':
                        shared_var['card_commands'] = shared_var['card_commands'] + tmp_card['names']
                        if help:
                            for name in tmp_card['names']:
                                bot.memory['card_help'][name] = help
                        
    bot.memory['card_commands'] = shared_var['card_commands']

@example('$refresh [luck/cards/triggers/capes]')
@commands('refresh', 'cache')
@priority('low')
def refresh(bot, trigger):
    """Forces the cache to update."""
    if not trigger.group(2) or trigger.group(2).lower() == 'cards':
        cache_cards(bot)
        return say(bot,"Card cache updated.")

def cards(bot, query, count = 0):
    global recursion_limit
    global recursions
    recursion_limit = 25
    recursions = 0
    
    def get_deck(key):
        if not isinstance(key, list):
            if key.lower() in shared_var['cards'] and len(shared_var['cards'][key.lower()])>0:
                return shared_var['cards'][key.lower()]
            if key.lower() in shared_var['cards_by_group'] and len(shared_var['cards_by_group'][key.lower()])>0:
                return shared_var['cards_by_group'][key.lower()]
            if key.lower() in shared_var['cards_by_keyword'] and len(shared_var['cards_by_keyword'][key.lower()])>0:
                return shared_var['cards_by_keyword'][key.lower()]
            return None
        else:
            decks = []
            for k in key:
                if k.lower() in shared_var['cards'] and len(shared_var['cards'][k.lower()])>0:
                    decks = decks + shared_var['cards'][k.lower()]
                if k.lower() in shared_var['cards_by_group'] and len(shared_var['cards_by_group'][k.lower()])>0:
                    decks = decks + shared_var['cards_by_group'][k.lower()]
                if k.lower() in shared_var['cards_by_keyword'] and len(shared_var['cards_by_keyword'][k.lower()])>0:
                    decks = decks + shared_var['cards_by_keyword'][k.lower()]
            if decks:
                return decks
            else:
                return None
                
    def process_card(card, prefix = []):
        global recursions
        recursions = recursions + 1
        if recursions > recursion_limit:
            return {'output': '', 'queue': []}
    
        new_queue = []
        text = card['text']
        
        #inline cards
        for index, value in enumerate(card['inline_cards']):
            keep = value[0].lower().startswith('keep!')
            if keep:
                value[0] = value[0][5:]
            subdeck = get_deck(value)
            if not subdeck:
                return say(bot,"Invalid card '"+' | '.join(value)+"'")
            else:
                options = [x for x in subdeck if x['id'] not in drawn_cards]
                if not options:
                    options = subdeck
                
                # Draw card by odds
                r = random.uniform(0, sum(item['odds'] for item in options))
                s = 0.0
                for x in options:
                    subcard = x
                    s += x['odds']
                    if r < s:
                        break
                
                response = process_card(subcard)
            
                if not keep:
                    drawn_cards.append(subcard['id'])
                
                insert = response['output']
                if value[0][0].isupper():
                    insert = insert[:1].upper() + insert[1:]

                text = text.replace('{'+str(index+1)+'}', insert)
                text = text.replace('{!'+str(index+1)+'}', insert.capitalize())
        
        #a(n) replacement
        match = shared_var['re_card_an'].search(text)
        number = 0
        while match and number<50:
            article = indefinite_article(match.group(2))
            text = text[:match.start(1)] + article + text[match.end(1):]
            match = shared_var['re_card_an'].search(text)
        
        #output
        output = ''.join(['['+x+'] ' for x in prefix])+text
        
        #additional cards
        sub_count = 0
        for subcard in card['cards']:
            show = True
            card_index = None
            primary = False if count>0 else True
            sep = False
            ending = False
            keep = False
            for tag in subcard['tags']:
                negate = False
                if tag and tag[0] == '!':
                    negate = True
                    t = tag[1:]
                else:
                    t = tag
                
                #Draw Order Rejection
                if t in positions:
                    if positions.index(t) >= count:
                        if negate:
                            show = False
                    elif not negate:
                        show = False
                
                #Sub-Draw Order Rejection
                if is_integer(t):
                    if sub_count >= int(t):
                        if not negate:
                            show = False
                    elif negate:
                        show = False
                
                #Percentage
                if t[-1] == '%' and is_float(t[:-1]):
                    target = float(t[:-1])
                    if random.uniform(0, 100.0)>target:
                        if not negate:
                            show = False
                    elif negate:
                        show = False
                        
                #Card Index
                if t[0] == '#':
                    if is_integer(t[1:]):
                        card_index = int(t[1:])
                    else:
                        card_index = t[1:]
                    
                #Separator
                if t == 'S':
                    sep = not negate
                    
                #Primary
                if t == 'P':
                    primary = not negate
                    
                #Primary
                if t == 'K':
                    keep = not negate
                        
            #Add to Queue
            if show:
                if sep and (count>1 or len(new_queue)>0):
                    new_queue.append(separator)
                new_queue.append({'key': subcard['keyword'], 'pre': subcard['preface'], 'card': card_index, 'primary': primary, 'keep': keep})
                sub_count = sub_count + 1

        return {'output': output, 'queue': new_queue}
        
    #Loop Through Queue
    queue = query
    for q in queue:
        if isinstance(q, dict) and 'primary' not in q:
            q['primary'] = True
    drawn_cards = []
    separator = '-------'
    positions = ['0th','1st','2nd','3rd','4th','5th','6th','7th','8th','9th','10th']
    while len(queue)>0 and count<16:
        data = queue.pop(0)
        if not isinstance(data, dict):
            if len(queue)>0 or data != separator:
                say(bot,data)
            continue
        
        if data['primary']: 
            count = count + 1
            
        deck = get_deck(data['key'])
        if not deck:
            return say(bot,"Invalid card '"+str(data['key'])+"'")
        else:
            if 'card' in data and data['card'] is not None:
                if isinstance(data['card'], int):
                    if data['card']>0 and data['card']<=len(deck):
                        card = deck[data['card']-1]
                    else:
                        return say(bot,"Invalid card '"+str(data['key'])+"' #"+str(data['card']))
                else:
                    options = [x for x in deck if data['card'].lower() in x['names'] and x['id'] not in drawn_cards]
                    if not options:
                        options = [x for x in deck if data['card'].lower() in x['names']]
                    if not options:
                        return say(bot,"Invalid card '"+str(data['key'])+"' "+'"'+str(data['card'])+'"')
                    card = random.choice(options)
            else:
                options = [x for x in deck if x['id'] not in drawn_cards]
                if not options:
                    options = deck
                    
                # Draw card by odds
                r = random.uniform(0, sum(item['odds'] for item in options))
                s = 0.0
                for x in options:
                    card = x
                    s += x['odds']
                    if r < s:
                        break
            
            response = process_card(card, data['pre'])
            
            if 'keep' not in data or not data['keep']:
                drawn_cards.append(card['id'])
                
            if response:
                queue = response['queue'] + queue
                say(bot,response['output'],3)
            else:
                return

@rule(r'.*')
@priority('low')
def card_commands(bot, trigger):
    if trigger[0] != '$':
        return
    data = shared_var['re_delimiters'].split(trigger.lower())
    command = data[0][1:]
    if command in shared_var['card_commands']:
        if len(data)==1:
            return cards(bot, [{'key': 'commands', 'pre': '', 'card': command, 'primary': False}], -1)
        else:
            list = []
            subcommand = command
            for key in data[1:]:
                #Check if command has its own sheet, or if it exists as a subcommand
                if command in shared_var['cards_by_group'] or command+' '+key in shared_var['card_sub_commands']:
                    card = {'key': command+' '+key, 'pre': ''}
                    list.append(card)
                #Check if card is a name
                elif subcommand in shared_var['card_sub_commands'] and subcommand+' '+key in shared_var['cards_by_name']:
                    card = {'key': subcommand, 'card': key, 'pre': ''}
                    list = [card]
                else:
                    return say(bot,"Card '"+command+' '+key+"' (or '"+subcommand+"' with name '"+key+"') missing.",3)
                subcommand = subcommand + ' ' + key
            return cards(bot, list)

@example('$card keyword [id]')
@commands('card')
@priority('low')
def card(bot, trigger):
    """Documentation can be found here: https://goo.gl/6icZb5"""

    if trigger.group(2):
        data = trigger.group(2).split(' ')
        if is_integer(data[-1]):
            cards(bot, [{'key': ' '.join(data[:-1]), 'pre': '', 'card': int(data[-1])}])
        elif data[-1][0] == '"' and data[-1][-1] == '"':
            cards(bot, [{'key': ' '.join(data[:-1]), 'pre': '', 'card': data[-1][1:-1].lower()}])
        else:
            cards(bot, [{'key': trigger.group(2), 'pre': ''}])
    else:
        return say(bot,"Please specify a card.")