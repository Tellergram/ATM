# coding=utf8
"""
admin.py - Willie Admin Module
Copyright 2010-2011, Sean B. Palmer (inamidst.com) and Michael Yanovich
(yanovich.net)
Copyright © 2012, Elad Alfassa, <elad@fedoraproject.org>
Copyright 2013, Ari Koivula <ari@koivu.la>

Licensed under the Eiffel Forum License 2.

http://willie.dftba.net
"""
from __future__ import unicode_literals

import willie.module
from willie.tools.time import pretty_date
import time

def configure(config):
    """
    | [admin] | example | purpose |
    | -------- | ------- | ------- |
    | hold_ground | False | Auto re-join on kick |
    """
    config.add_option('admin', 'hold_ground', "Auto re-join on kick")

@willie.module.commands('users')
@willie.module.priority('medium')
@willie.module.example('$users #Weaverdice')
@willie.module.admin
def users(bot, trigger):
    """Lists all users of a channel the bot is in. This is an admin-only command."""
    # Can only be done in privmsg
    if not trigger.is_privmsg:
        return
    
    # Can only be done by an admin
    if not trigger.admin:
        return
        
    if not trigger.group(3):
        return bot.say("You must provide a channel.")
        
    channel = trigger.group(3).lower()
        
    if channel not in bot.privileges:
        return bot.say("I am not in that channel.")
               
    user_list = []
    for user in bot.privileges[channel].keys():
        nick = user
        if bot.privileges[channel][nick] == willie.module.VOICE:
            nick = '+' + nick
            
        if bot.privileges[channel][nick] == willie.module.HALFOP:
            nick = '%' + nick
            
        if bot.privileges[channel][nick] == willie.module.OP:
            nick = '@' + nick
            
        if bot.privileges[channel][nick] == willie.module.ADMIN:
            nick = '&' + nick
            
        if bot.privileges[channel][nick] == willie.module.OWNER:
            nick = '~' + nick

        user_list.append(nick)
               
    return bot.say(", ".join(user_list),10)
    
@willie.module.commands('channels')
@willie.module.priority('medium')
@willie.module.example('$channels')
@willie.module.admin
def channels(bot, trigger):
    """Lists all channels the bot is in. This is an admin-only command."""
    # Can only be done in privmsg by an admin
    if not trigger.is_privmsg:
        return
        
    if trigger.admin:
        channel_list = []
        for c in bot.privileges.keys():
            if 'channel_timer_dict' in bot.memory and c.lower() in bot.memory['channel_timer_dict']:
                channel_list.append("%s (%s): %i" % (c, pretty_date(bot.memory['channel_timer_dict'][c.lower()]), len(bot.privileges[c])))
            else:
                channel_list.append("%s (?): %i" % (c, len(bot.privileges[c])))
        
        return bot.say(" | ".join(channel_list),10)
    
@willie.module.commands('goto')
@willie.module.priority('medium')
@willie.module.example('$goto #example or $goto #example key')
@willie.module.admin
def join(bot, trigger):
    """Join the specified channel. This is an admin-only command."""
    # Can only be done in privmsg by an admin
    if not trigger.is_privmsg:
        return

    if trigger.admin:
        channel, key = trigger.group(3), trigger.group(4)
        if not channel:
            return
        elif not key:
            bot.join(channel)
            bot.memory['channel_timer_dict'][channel] = time.time()
        else:
            bot.join(channel, key)
            bot.memory['channel_timer_dict'][channel] = time.time()


@willie.module.commands('part')
@willie.module.priority('low')
@willie.module.example('.part #example')
@willie.module.admin
def part(bot, trigger):
    """Part the specified channel. This is an admin-only command."""
    # Can only be done in privmsg by an admin
    if not trigger.is_privmsg:
        return
    if not trigger.admin:
        return

    channel, _sep, part_msg = trigger.group(2).partition(' ')
    if part_msg:
        bot.part(channel, part_msg)
    else:
        bot.part(channel)


@willie.module.commands('quit')
@willie.module.priority('low')
@willie.module.admin
def quit(bot, trigger):
    """Quit from the server. This is an owner-only command."""
    # Can only be done in privmsg by the owner
    if not trigger.is_privmsg:
        return
    if not trigger.owner:
        return

    quit_message = trigger.group(2)
    if not quit_message:
        quit_message = 'Quitting on command from %s' % trigger.nick

    bot.quit(quit_message)


@willie.module.commands('msg')
@willie.module.priority('low')
@willie.module.example('.msg #YourPants Does anyone else smell neurotoxin?')
@willie.module.admin
def msg(bot, trigger):
    """
    Send a message to a given channel or nick. Can only be done in privmsg by an
    admin.
    """
    if not trigger.is_privmsg:
        return
    if not trigger.admin:
        return
    if trigger.group(2) is None:
        return

    channel, _sep, message = trigger.group(2).partition(' ')
    message = message.strip()
    if not channel or not message:
        return

    bot.msg(channel, message)


@willie.module.commands('me')
@willie.module.priority('low')
@willie.module.admin
def me(bot, trigger):
    """
    Send an ACTION (/me) to a given channel or nick. Can only be done in privmsg
    by an admin.
    """
    if not trigger.is_privmsg:
        return
    if not trigger.admin:
        return
    if trigger.group(2) is None:
        return

    channel, _sep, action = trigger.group(2).partition(' ')
    action = action.strip()
    if not channel or not action:
        return

    msg = '\x01ACTION %s\x01' % action
    bot.msg(channel, msg)


@willie.module.event('INVITE')
@willie.module.rule('.*')
@willie.module.priority('low')
def invite_join(bot, trigger):
    """
    Join a channel willie is invited to, if the inviter is an admin.
    """
    if not trigger.admin:
        return
    bot.join(trigger.args[1])


@willie.module.event('KICK')
@willie.module.rule(r'.*')
@willie.module.priority('low')
def hold_ground(bot, trigger):
    """
    This function monitors all kicks across all channels willie is in. If it
    detects that it is the one kicked it'll automatically join that channel.

    WARNING: This may not be needed and could cause problems if willie becomes
    annoying. Please use this with caution.
    """
    if bot.config.has_section('admin') and bot.config.admin.hold_ground:
        channel = trigger.sender
        if trigger.args[1] == bot.nick:
            bot.join(channel)


@willie.module.commands('mode')
@willie.module.priority('low')
@willie.module.admin
def mode(bot, trigger):
    """Set a user mode on Willie. Can only be done in privmsg by an admin."""
    if not trigger.is_privmsg:
        return
    if not trigger.admin:
        return
    mode = trigger.group(3)
    bot.write(('MODE ', bot.nick + ' ' + mode))


@willie.module.commands('set')
@willie.module.example('.set core.owner Me')
@willie.module.admin
def set_config(bot, trigger):
    """See and modify values of willies config object.

    Trigger args:
        arg1 - section and option, in the form "section.option"
        arg2 - value

    If there is no section, section will default to "core".
    If value is None, the option will be deleted.
    """
    if not trigger.is_privmsg:
        bot.reply("This command only works as a private message.")
        return
    if not trigger.admin:
        bot.reply("This command requires admin priviledges.")
        return

    # Get section and option from first argument.
    arg1 = trigger.group(3).split('.')
    if len(arg1) == 1:
        section, option = "core", arg1[0]
    elif len(arg1) == 2:
        section, option = arg1
    else:
        bot.reply("Usage: .set section.option value")
        return

    # Display current value if no value is given.
    value = trigger.group(4)
    if not value:
        if not bot.config.has_option(section, option):
            bot.reply("Option %s.%s does not exist." % (section, option))
            return
        # Except if the option looks like a password. Censor those to stop them
        # from being put on log files.
        if option.endswith("password") or option.endswith("pass"):
            value = "(password censored)"
        else:
            value = getattr(getattr(bot.config, section), option)
        bot.reply("%s.%s = %s" % (section, option, value))
        return

    # Otherwise, set the value to one given as argument 2.
    setattr(getattr(bot.config, section), option, value)


@willie.module.commands('save')
@willie.module.example('.save')
@willie.module.admin
def save_config(bot, trigger):
    """Save state of willies config object to the configuration file."""
    if not trigger.is_privmsg:
        return
    if not trigger.admin:
        return
    bot.config.save()
