# coding=utf8
"""
seen.py - Willie Seen Module
Copyright 2008, Sean B. Palmer, inamidst.com
Copyright 2012, Elad Alfassa <elad@fedoraproject.org>
Licensed under the Eiffel Forum License 2.
http://willie.dftba.net
"""
from __future__ import unicode_literals

import time
from datetime import datetime
from willie.module import commands, rule, priority, interval
from willie.tools import storage
from willie.tools.time import pretty_date

def setup(bot):
	data = storage.get('seen')
	if data and isinstance(data,dict):
		bot.memory['seen_dict'] = data
	else:
		bot.memory['seen_dict'] = {}

@interval(600)
def save(bot):
	storage.put('seen',bot.memory['seen_dict'])
		
@commands('seen')
def seen(bot, trigger):
	"""Reports when and where the user was last seen. Use * on the end of [recipient] to match multiple nicks (e.g Tell*)"""
	if not trigger.group(2):
		return bot.say("Seen whom?")
	nick = trigger.group(2).strip().lower()
	if nick == str(trigger.nick).lower():
		return bot.action('holds up a mirror.')
		
	if nick == bot.nick.lower() or nick == 'cashy':
		return bot.say("I'm right here.")
	
	true_nick = None
	if not nick.endswith('*'):
		if nick in bot.memory['seen_dict']:
			true_nick = nick
			nick_string = trigger.group(2).strip()
	else:
		start = nick.rstrip('*:')
		test_time = 0
		for n in bot.memory['seen_dict'].keys():
			if n.startswith(start) and bot.memory['seen_dict'][n]['timestamp']>test_time and n != str(trigger.nick).lower():
				test_time = bot.memory['seen_dict'][n]['timestamp']
				true_nick = n
				
	if true_nick:
		if 'name' in bot.memory['seen_dict'][true_nick]:
			name = bot.memory['seen_dict'][true_nick]['name']
		else:
			name = true_nick
		if bot.memory['seen_dict'][true_nick]['channel'].lower() == trigger.sender.lower():
			message = bot.memory['seen_dict'][true_nick]['message']
			if len(message) > 100: message = message[:97]+'...'
			msg = "I saw %s %s, saying '%s'" % (name, pretty_date(bot.memory['seen_dict'][true_nick]['timestamp']), message)
		else:
			msg = "I saw %s %s in another channel." % (name, pretty_date(bot.memory['seen_dict'][true_nick]['timestamp']))
		bot.say(str(trigger.nick) + ': ' + msg)
	else:
		bot.say("I've never seen %s." % trigger.group(2).strip())

@rule('(.*)')
@priority('low')
def note(bot, trigger):
	if not trigger.is_privmsg:
		nick = str(trigger.nick).lower()
		bot.memory['seen_dict'][nick] = {
			'timestamp': time.time(),
			'name': trigger.nick,
			'channel': str(trigger.sender),
			'message': trigger
		}