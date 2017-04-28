'''
Created on May 19, 2013

@author: daniel

Helper functions
'''

import hashlib


def get_chat_id(chat):
    """
    get a unique id of a chat
        
    :param skype4Pi.chat.Chat instance
    """
    
    m = hashlib.sha1()
    m.update(chat.Name)
    return m.hexdigest()