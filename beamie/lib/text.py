#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

def generate_random_string(length=None, alphabet=None):
    """Static function that generates a random password salt
 
    :param length: How many digits of salt to generate
    :type length: int
    :returns: A randomly generated salt string
    :rtype: str
    """
 
    if alphabet is None:
        alphabet = "".join([
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "0123456789",
            "!@#$%^&*()-=_+[]{};:<>/?"
        ])  
 
    if length is None:
        length = random.randint(1, 32) 
 
    return "".join([ random.choice(alphabet) for _character in range(length) ])

def generate_salt():
    return generate_random_string(random.randint(12,32))

