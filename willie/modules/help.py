# coding=utf8
"""
help.py - Willie Help Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright © 2013, Elad Alfassa, <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.

http://willie.dftba.net
"""
from __future__ import unicode_literals

from willie.module import commands, rule, example, priority
from willie.tools import iterkeys

def setup(bot=None):
    if not bot:
        return
		
	if 'card_commands' not in bot.memory:
		bot.memory['card_commands'] = []

    if (bot.config.has_option('help', 'threshold') and not
            bot.config.help.threshold.isdecimal()):  # non-negative integer
        from willie.config import ConfigurationError
        raise ConfigurationError("Attribute threshold of section [help] must be a nonnegative integer")


@rule('$nick' '(?i)(help|doc) +([A-Za-z]+)(?:\?+)?$')
@example('$help roll')
@commands('help')
@priority('low')
def help(bot, trigger):
    """Shows a command's documentation, and possibly an example."""
    if not trigger.group(2):
        bot.reply('Type $help <command> (for example $help roll) to get help for a command, or $commands for a list of commands.')
    else:
        name = trigger.group(2)
        name = name.lower()

        if bot.config.has_option('help', 'threshold'):
            threshold = int(bot.config.help.threshold)
        else:
            threshold = 3

        if name in bot.doc:
            if len(bot.doc[name][0]) + (1 if bot.doc[name][1] else 0) > threshold:
                if trigger.nick != trigger.sender:  # don't say that if asked in private
                    bot.reply('The documentation for this command is too long; I\'m sending it to you in a private message.')
                msgfun = lambda l: bot.msg(trigger.nick, l)
            else:
                msgfun = bot.reply

            for line in bot.doc[name][0]:
                msgfun(line)
            if bot.doc[name][1]:
                msgfun('e.g. ' + bot.doc[name][1])
        elif name in bot.memory['card_commands']:
            if name in bot.memory['card_help']:
                bot.reply(bot.memory['card_help'][name])
            else:				
                bot.reply('No help is available for this command.')

@commands('commands')
@priority('low')
def commands(bot, trigger):
    """Return a list of bot's commands"""
    commands = bot.doc.keys()
    if not trigger.admin:
        commands = [x for x in commands if bot.doc[x][2] == False]
    
    names = ', '.join(sorted(commands + bot.memory['card_commands']))
	
    if not trigger.is_privmsg:
        bot.reply("I am sending you a private message of all my commands!")
    bot.msg(trigger.nick, 'Commands I recognise: ' + names + '.', max_messages=10)
    bot.msg(trigger.nick, "For help, do '$help example' where example is the name of the command you want help for.")

@rule('$nick' r'(?i)help(?:[?!]+)?$')
@priority('low')
def help2(bot, trigger):
    bot.reply('I\'m Teller\'s bot. Say "$commands" to me in private for a list of my commands.')