# coding=utf8
"""
vote.py - Willie Dice Module
Copyright 2015, Teller
"""
from __future__ import unicode_literals
from willie.module import commands, example, priority, thread, interval, rule

def setup(bot):
    bot.memory['votes'] = {}
        
@example('$votes [drop] [voter]')
@commands('votes')
@priority('low')
def votes(bot, trigger):
    """Displays a list of all votes. '$votes drop' clears all votes from memory. '$votes drop [voter]' removes the vote of a specific voter"""
    if trigger.group(2):
        if trigger.group(2) == "drop":
            bot.memory['votes'] = {}
            return bot.say("All votes dropped.")
        else:
            data = trigger.group(2).split(' ',1)
            if data[0] == "drop":
                try:
                    del bot.memory['votes'][data[1]]
                    return bot.say("'"+data[1]+"' vote dropped.")
                except KeyError:
                    return bot.say(data[1]+" has not voted.")
            else:
                return bot.say("Invalid input.")
    else:
        if bot.memory['votes']:
            output = {}
            for key in bot.memory['votes']:
                vote = bot.memory['votes'][key]
                if vote not in output:
                    output[vote] = 1
                else:
                    output[vote] = output[vote] + 1
            list = sorted(output, key=output.get, reverse=True)
            final = []
            for l in list:
                final.append('['+l+' x'+str(output[l])+']')
            
            return bot.say(' '.join(final))
        else:
            return bot.say("No votes registered.")
    
    
@example('$vote [vote/drop]')
@commands('vote')
@priority('low')
def vote(bot, trigger):
    """Sets your vote to the provided text. '$vote drop' removes your vote from memory."""
    if trigger.group(2):
        if trigger.group(2) == "drop":
            bot.memory['votes'].pop(trigger.nick+'', None)
            return bot.say("Vote dropped.")
        else:
            if trigger.nick.lower() != trigger.group(2).lower().strip():
                bot.memory['votes'][trigger.nick+''] = trigger.group(2).strip()
                return bot.say("Vote registered.")
            else:
                return bot.say("You cannot vote for yourself.")
    else:
        return bot.say("Please provide your vote.")
    
@example('$voters')
@commands('voters')
@priority('low')
def voters(bot, trigger):
    """Outputs a list of voters."""
    if bot.memory['votes']:
        return bot.say(', '.join(bot.memory['votes'].keys()))
    else:
        return bot.say("No voters registered.")