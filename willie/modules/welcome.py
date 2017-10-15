# coding=utf8
"""
welcome.py - Willie Dice Module
Copyright 2015, Teller
"""
from __future__ import unicode_literals
from willie.module import commands, example, priority, interval
import random, re, time
from willie.tools import common, storage

def setup(bot):
    data = storage.get('welcome')
    if data and isinstance(data,dict):
        bot.memory['welcome_dict'] = data
    else:
        bot.memory['welcome_dict'] = {}

@interval(600)
def save(bot):
	storage.put('welcome',bot.memory['welcome_dict'])
        
@example('$welcome [nick]')
@commands('welcome')
@priority('low')
def welcome(bot, trigger):
    """Welcomes new members to the channel."""

    if trigger.sender.lower() != '#weaverdice':
        return bot.say('Please perform welcomes in #Weaverdice.')

    if trigger.group(2):
        nick = common.nick_online(bot, trigger.group(2))
        if nick:
            if nick.lower() not in bot.memory['welcome_dict'] or time.time() - bot.memory['welcome_dict'][nick.lower()]['timestamp'] > 1209600:
                bot.msg(nick, "Hi %s. Welcome to #Weaverdice, the channel for Worm RP. Check out this link for some useful information about the channel and the game: https://goo.gl/sQWXHb" % (nick))
                bot.memory['welcome_dict'][nick.lower()] = {
                    'timestamp': time.time(),
                    'name': nick
                }
                return bot.say("Done!")
            else:
                return bot.say("I already welcomed %s." % (nick))
        else:
            return bot.say("I don't see that person.")
    else:
        return bot.say("Welcome whom?")