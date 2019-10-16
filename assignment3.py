#!/usr/local/bin/python3
## Assignment3
## File description:
##

import re
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords

# nltk.download('stopwords')

def readFiles(filename):
    f = open(filename, "r")
    data = f.read()
    return data

def cleanText(text):
    text = text.lower() #Lowercase Text
    text = re.sub(r'<\/?[\w ="-:;]*>', '', text) #Remove HTML Tags
    text = re.sub(r'&#\d{2,4};', '', text) #Remove HTML Numbers
    text = re.sub(r'[^\w\s]','', text) #Remove punctuation
    text = re.sub(r'[\n]', ' ', text) #Replace \n by space
    text = re.sub(r'[\t]', '', text) #Remove \t

    tokenized_text = word_tokenize(text) #Tokenizetext

    filtered_text = []
    stop_words = set(stopwords.words('english'))
    #Remove stopwords
    for i in range(len(tokenized_text)):
        if not tokenized_text[i] in stop_words:
            filtered_text.append(tokenized_text[i])

    return filtered_text

print(cleanText(readFiles("test_text")))
