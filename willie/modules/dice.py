# coding=utf8
"""
dice.py - Willie Dice Module
Copyright 2015, Teller
"""
from __future__ import unicode_literals
from willie.module import commands, example, priority
import random, re
from willie.tools import common

def setup(bot):
    bot.memory['Dice_MINROLLS'] = 1
    bot.memory['Dice_MAXROLLS'] = 50
    bot.memory['Dice_MINSIDES'] = 1
    bot.memory['Dice_MAXSIDES'] = 1000
    bot.memory['Dice_REGEX'] = re.compile("^([0-9]*)([dhlDHL])([0-9]+)([hlHL][0-9]+)?([\+-][0-9]+)?(!)?([Xx][0-9]{1,2})?(!)?(.*?)(?:\[([Bb]?[Cc]{2}) (.+)\])?$")

@commands('roll')
@priority('low')
def roll(bot, trigger):
    """
    Rolls a die or dice. Examples:
    2d10              Rolls 2 dice with 10 sides. Final result is their sum.
    3h6               Rolls 3 dice with 6 sides. Final result is the highest die.
    3l20              Rolls 3 dice with 20 sides. Final result is the lowest die.
    1d6+3             Rolls 1 die with 6 sides. Final result is the die plus 3.
    3d7+3!            Rolls 3 dice with 7 sides. Final result is their sum, with 3 added to each die.
    3d6x4             Rolls 3 dice with 6 sides. Repeats this 4 times and shows each result.
    3d30h2            Rolls 3 dice with 30 sides and takes the two highest. Final result is their sum.
    3d4l2             Rolls 3 dice with 4 sides and takes the two lowest. Final result is their sum.
    1d6 Social        Rolls 1 die with 6 sides. Final result is the roll. Will be tagged with "Social".
    10d8 ABC [CC Bob] Rolls 10 dice with 8 sides. Final result is the roll. Will be tagged with "ABC", and the result will be shared with 'Bob'.
    10d8 ABC [BCC Bob] Same as CC, but the result is only shown to 'Bob'.
    """
    if not trigger.group(2):
        return bot.say('Pick a die.')
    eval = bot.memory['Dice_REGEX'].match(trigger.group(2))
    if not eval:
        return bot.say('Invalid roll.')
        
    #Number
    number = eval.group(1)
    if number:
        number = int(number)
    else:
        number = 1

    if number<bot.memory['Dice_MINROLLS'] or number>bot.memory['Dice_MAXROLLS']:
        return bot.say('Number of dice must be between ' + str(bot.memory['Dice_MINROLLS']) + ' and ' + str(bot.memory['Dice_MAXROLLS']) + '.')
    
    #Type
    select = number
    highest = True
    if eval.group(2).lower() == 'h':
        select = 1
        
    if eval.group(2).lower() == 'l':
        select = 1
        highest = False
    
    type = eval.group(2).lower()
    
    #Sides
    sides = int(eval.group(3))
    
    if sides<bot.memory['Dice_MINSIDES'] or sides>bot.memory['Dice_MAXSIDES']:
        return bot.say('Number of sides must be between ' + str(bot.memory['Dice_MINSIDES']) + ' and ' + str(bot.memory['Dice_MAXSIDES']) + '.')
    
    #Highest/Lowest
    if eval.group(4):
        select = max(0,min(number,int(eval.group(4)[1:])))
        if eval.group(4)[0].lower() == 'l':
            highest = False
    
    #Bonus
    bonus = eval.group(5)
    if bonus:
        bonus = int(bonus)
        if bonus<0:
            bonus_string=str(bonus)
        else:
            bonus_string='+'+str(bonus)
    else:
        bonus = 0
        bonus_string = ''
        
    if (eval.group(6) or eval.group(8)) and number>1:
        bonus_all = True
    else:
        bonus_all = False
        
    #Multiply
    if eval.group(7):
        multiply = int(eval.group(7)[1:])
        if multiply == 0:
            return bot.say('-_-')
        if multiply > 16:
            return bot.say('Number of reptitions must be 16 or lower.')
    else: 
        multiply = 1
    
    #Tag
    tag = eval.group(9)
    
    #CC
    cc = eval.group(10)
    
    #CC Target
    cc_target = eval.group(11)
        
    #build response
    response = trigger.nick
    if tag:
        if tag.strip():
            response = response + ' "' + tag.strip() + '"'
        
    for roll_number in range(0, multiply):
        
        #roll all of the necessary dice
        dice = [{'roll': random.randint(1,sides), 'index': x} for x in range(0, number)]
        
        if select == number:
            selected = range(0, number)
        else:
            selected = []
            sort = sorted(dice, key=lambda k: k['roll'], reverse=highest)
            for s in range(0, select):
                selected.append(sort[s]['index'])
            
        if bonus_all:
            total = []
        else:
            total = [bonus]
        
        for index, d in enumerate(dice, start=0):
            if index in selected:
                response = response + ' [' + str(d['roll']) + ']'
                if bonus_all:
                    response = response + bonus_string
                    total.append(d['roll']+bonus)
                else:
                    total[0] = total[0] + d['roll']
            else:
                response = response + ' (' + str(d['roll']) + ')'
                if bonus_all: response = response + bonus_string
        
        if not bonus_all:
            response = response + ' '+bonus_string
        
        response = response + ' = ' + ', '.join(str(x) for x in total)
        
        if roll_number<multiply-1:
            response = response + '  :: '
    
    if not cc or cc.lower()!='bcc':
        bot.say(response)
    
    if cc_target:
        cc_message = response + " (Command was '%s %s')" % (cc, trigger.group(2).split()[0])
        nick = common.inform(bot, bot.nick, cc_target, cc_message)
        if nick:
            bot.say("Roll sent to "+nick+".")
        else:
            bot.say("Roll will be sent to "+cc+" when I see them.")