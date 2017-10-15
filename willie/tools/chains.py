# coding=utf8
"""Functions for determining admins."""
from __future__ import unicode_literals
from __future__ import absolute_import

def admins(bot):
    admins = ["teller", "tell", "telloff", "teller|gm", "dolyn", "dol", "dol|mobile", "dol|afk"]
    try:
        for user in bot.privileges["#weaverdice"].keys():
            if bot.privileges["#weaverdice"][user] > 1:
                admins.append(user.lower())
    except:
        pass
    return admins