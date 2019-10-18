#!/usr/local/bin/python3
## Assignment3
## File description:
##

import re
import nltk
import requests
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords

# nltk.download('stopwords')

def readFile(filename):
    f = open(filename, "r")
    data = []
    for line in f.readlines():
        line = re.sub(r'[\n]', '', line)
        data.append(line)
    return data

def downloadURL(url):
    print('Downloading page')
    res = requests.get(url)
    if res.status_code == 200:
        print('Download Success!')
    elif res.status_code == 404:
        print('Error 404 with URL ', url, ' : Not Found.')
    else:
        print('Error ', res.status_code, 'on URL : ', url)
    return res.content

def getDivContent(page):
    soup = BeautifulSoup(page, 'html.parser')
    return(soup.find(class_="post-content").find_all('p'))

def cleanText(text):
    print("Cleaning Text")
    text = text.lower() #Lowercase Text
    text = re.sub(r'<\/?[\w ="-:;]*>', '', text) #Remove HTML Tags
    text = re.sub(r'&#8217;',' \'', text) #Transform apostrophes
    text = re.sub(r'&#\d{2,4};', '', text) #Remove HTML Numbers
    text = re.sub(r'[^\w\s\']','', text) #Remove punctuation
    text = re.sub(r'[\n]', ' ', text) #Replace \n by space
    text = re.sub(r'[\t]', '', text) #Remove \t

    tokenized_text = word_tokenize(text) #Tokenizetext

    filtered_text = []
    stop_words = set(stopwords.words('english'))
    #Remove stopwords
    for i in range(len(tokenized_text)):
        if not tokenized_text[i] in stop_words:
            filtered_text.append(tokenized_text[i])
    print("Done.")
    return filtered_text

url_list = readFile("url_list.txt")
page = downloadURL(url_list[0])

# print(getDivContent(page))
content = getDivContent(page)
print(cleanText(str(content[len(content) - 1])))

