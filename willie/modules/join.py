# coding=utf8
"""
join.py - Willie Join Module
Copyright 2015, Teller
http://willie.dftba.net
"""

from __future__ import unicode_literals

import time
from willie.module import commands, rule, example, priority, interval
from willie.tools import iterkeys
from willie.tools import storage
from willie.tools import chains
import threading

def setup(bot):    
    data = storage.get('channel_timer')
    if data and isinstance(data,dict):
        bot.memory['channel_timer_dict'] = data
    else:
        bot.memory['channel_timer_dict'] = {}
    bot.memory['channel_timer_lock'] = threading.Lock()

@interval(600)
def save(bot):
    bot.memory['channel_timer_lock'].acquire()
    try:
        #Save list of channels
        channels = [c.lower() for c in bot.privileges.keys()]
        if channels:
            bot.config.core.channels = channels
            bot.config.save()
            
            #match timer list
            new_keys = {}
            for c in channels:
                new_keys[c] = time.time()
                
            for c in bot.memory['channel_timer_dict'].keys():
                if c in new_keys.keys():
                    new_keys[c] = bot.memory['channel_timer_dict'][c]
            
            bot.memory['channel_timer_dict'] = new_keys
    finally:
        bot.memory['channel_timer_lock'].release()
        
    #Save channel timers
    storage.put('channel_timer',bot.memory['channel_timer_dict'])
    
@interval(3600)
def autoleave(bot):
    for c in bot.memory['channel_timer_dict'].keys():
        if time.time()-bot.memory['channel_timer_dict'][c]>3600*24*14 and (c != '#weaverdice' and c != '#gamedesign'):
            bot.part(c)

@example('$join #WormGrantsville')
@commands('join')
@priority('low')
def join_on_invite(bot, trigger):
    if trigger.group(2):
        channel = trigger.group(2).lower()
        prefix_list = ('#wd','#worm','#pd','#pact')
        exception_list = ('#pactdice','#weaverdice','#gamedesign','#motorcity','#other')
        user_list = chains.admins(bot)
        if channel.startswith(prefix_list) or channel in exception_list or trigger.nick.lower() in user_list:
            bot.join(channel)
            bot.memory['channel_timer_dict'][channel] = time.time()
        else:
            bot.reply("I only join channels that start with '#WD', '#Worm', '#PD', or '#Pact', sorry.")
    else:
            bot.reply("Specify a channel.")
            
@example('$leave')
@commands('leave')
@commands('part')
@priority('low')
def leave(bot, trigger):
    channel = trigger.sender.lower()
    if channel == '#weaverdice' or channel == '#gamedesign':
        bot.say("No.")
    else:
        bot.part(trigger.sender)
        
@rule('(.*)')
@priority('low')
def note(bot, trigger):
    if not trigger.is_privmsg:
        channel = trigger.sender.lower()
        bot.memory['channel_timer_dict'][channel] = time.time()