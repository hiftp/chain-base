# -*- coding: utf-8 -*-
from slugify import slugify
import string
import os
import re

def count_alphabet():
    """
    Return dict which contains rating of alplabet
    """
    # Get all txt file in folder data
    list_file = []
    for file in os.listdir("data"):
        if file.endswith(".txt"):
            list_file.append(os.path.join("data", file))
    # Int result
    result = {}
    for i in string.ascii_lowercase:
        result[i] = 0
    # Counting
    for file in list_file:
        f = open(file, 'r')
        content = f.read()
        content = slugify(content)
        content = content.replace("-", '')
        for char in content:
            if char in result.keys():
                result[char] = result[char] + 1
        f.close()
    # Compute total
    total = 0
    for k in result.keys():
        total = total + result[k]
    # Compute 
    for k in result.keys():
        result[k] = 100.0 * result[k] / total 
    return result
    
print(count_alphabet())