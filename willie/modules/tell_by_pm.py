# coding=utf8
"""
tell.py - Willie Tell and Ask Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright 2015, Teller, #WeaversDice on irc.darklordpotter.net
Modified by 
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net
"""
from __future__ import unicode_literals

import os
import time
import threading
import sys
from willie.tools import Identifier, iterkeys
from willie.module import commands, nickname_commands, rule, priority, example
from willie.tools import storage
from willie.tools.time import pretty_date

def setup(bot):
    data = storage.get('tell')
    if data and isinstance(data,dict):
        bot.memory['tell_dict'] = data
    else:
        bot.memory['tell_dict'] = {}
    bot.memory['tell_lock'] = threading.Lock()

@commands('watch')
@nickname_commands('watch')
@example('$watch [nick]')
def watch(bot, trigger):
    """Receive a notification when a user speaks. Use * on the end of [nick] to match multiple nicks (e.g Tell*)"""
    
    if trigger.is_privmsg is False:
        return bot.reply("This command only works in PMs.")
        
    teller = trigger.nick
    verb = trigger.group(1)
    
    if not trigger.group(3):
        bot.reply("%s whom?" % verb)
        return
        
    tellee = trigger.group(3).rstrip('.,:;')
    
    tellee = Identifier(tellee)

    if len(tellee) > 20:
        return bot.reply('That nickname is too long.')
    if tellee == bot.nick or tellee == 'Cashy':
        return bot.reply("[-_-]")

    if not tellee in (Identifier(teller), bot.nick, 'me'):
        timenow = time.time()
        bot.memory['tell_lock'].acquire()
        try:
            if not tellee in bot.memory['tell_dict']:
                bot.memory['tell_dict'][tellee] = [(teller, verb, timenow, '')]
            else:
                found = False
                for (_teller, _verb, _datetime, _msg) in bot.memory['tell_dict'][tellee]:
                    if verb.lower()=='watch':
                        if _teller == teller:
                            found = True
                            break
                if found:
                    return bot.say("You already have me watching for %s." % tellee)
                else:
                    bot.memory['tell_dict'][tellee].append((teller, verb, timenow, ''))
        finally:
            bot.memory['tell_lock'].release()

        bot.reply("I'll let you know when I see %s." % tellee)
    elif Identifier(teller) == tellee:
        bot.say('[-_-]')
    else:
        bot.say("[-_-]")

    storage.put('tell',bot.memory['tell_dict'])
 
@commands('tell')
@nickname_commands('tell')
@example('$tell [nick] [message]')
def tell(bot, trigger):
    """Give someone a message the next time they're seen. Use * on the end of [recipient] to match multiple nicks (e.g Tell*)"""
    
    if trigger.is_privmsg is False:
        return bot.reply("This command only works in PMs.")

    teller = trigger.nick
    verb = trigger.group(1)

    if not trigger.group(3):
        bot.reply("%s whom?" % verb)
        return

    tellee = trigger.group(3).rstrip('.,:;')
    msg = trigger.group(2).lstrip(tellee).lstrip()

    if not msg:
        bot.reply("%s %s what?" % (verb, tellee))
        return

    tellee = Identifier(tellee)

    if len(tellee) > 20:
        return bot.reply('That nickname is too long.')
    if tellee == bot.nick or tellee == 'Cashy':
        return bot.reply("I'm right here.")

    if not tellee in (Identifier(teller), bot.nick, 'me'):
        timenow = time.time()
        bot.memory['tell_lock'].acquire()
        try:
            if not tellee in bot.memory['tell_dict']:
                bot.memory['tell_dict'][tellee] = [(teller, verb, timenow, msg)]
            else:
                bot.memory['tell_dict'][tellee].append((teller, verb, timenow, msg))
        finally:
            bot.memory['tell_lock'].release()

        bot.reply("I'll pass that on when %s is around." % tellee)
    elif Identifier(teller) == tellee:
        bot.say('You can %s yourself that.' % verb)
    else:
        bot.say("[-_-]")

    storage.put('tell',bot.memory['tell_dict'])


@rule('(.*)')
@priority('low')
def message(bot, trigger):
    tellee = trigger.nick
    channel = trigger.sender

    tells = []
    nicks = list(reversed(sorted(bot.memory['tell_dict'].keys())))

    for nick in nicks:
        if tellee.lower() == nick.lower() or (nick.endswith('*') and tellee.lower().startswith(nick.lower().rstrip('*:'))):
            bot.memory['tell_lock'].acquire()
            try:
                new_key = []
                for (teller, verb, datetime, msg) in bot.memory['tell_dict'][nick]:
                    if verb.lower()=='tell':
                        tells.append("[Sent %s] <%s> %s" % (pretty_date(datetime), teller, msg))
                    if verb.lower()=='inform':
                        tells.append("[I] [Sent %s] <%s> %s" % (pretty_date(datetime), teller, msg))
                    elif verb.lower()=='watch':
                        if trigger.is_privmsg is False:
                            if teller in bot.privileges[channel]:
                                bot.msg(teller, "%s just spoke in %s." % (tellee, channel))
                            else:
                                bot.msg(teller, "%s just spoke in a channel you aren't in." % (tellee))
                        else:
                            if datetime-time.time()<86400:
                                new_key.append((teller, verb, datetime, msg))
                if new_key:
                    bot.memory['tell_dict'][nick] = new_key
                else:
                    try:
                        del bot.memory['tell_dict'][nick]
                    except KeyError:
                        bot.msg(channel, 'Er...')
            finally:
                bot.memory['tell_lock'].release()

    for line in tells:
        bot.msg(tellee, line)

    storage.put('tell',bot.memory['tell_dict'])