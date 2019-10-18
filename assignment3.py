#!/usr/local/bin/python3
## Assignment3
## File description:
##

import re
import nltk
import requests
import pickle
import os.path
import sklearn
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer

# nltk.download('stopwords')

def readFile(filename):
    f = open(filename, "r")
    data = []
    for line in f.readlines():
        line = re.sub(r'[\n]', '', line)
        data.append(line)
    return data

def downloadURL(url):
    print('Downloading page :', url)
    res = requests.get(url)
    if res.status_code == 200:
        print('Download Success!')
    elif res.status_code == 404:
        print('Error 404 with URL ', url, ' : Not Found.')
    else:
        print('Error ', res.status_code, 'on URL : ', url)
    return res.content

def pickleFile(filename, pages_dict):
    print("Pickling File")
    f = open(filename, 'wb')
    pickle.dump(pages_dict, f)
    f.close()
    print("File pickled")

def unpickleFile(filename):
    print("Unpickling File")
    f = open(filename, 'rb')
    new_dict = pickle.load(f)
    f.close()
    print("File unpickled")
    return new_dict

def getDivContent(page):
    soup = BeautifulSoup(page, 'html.parser')
    post_content = soup.find(class_="post-content").find_all('p')
    post_content = ' '.join(map(str, post_content))
    return(post_content)

def cleanText(text):
    print("Cleaning Text")
    text = text.lower() #Lowercase Text
    text = re.sub(r'<\/?[\w ="-:;]*>', '', text) #Remove HTML Tags
    # text = re.sub(r'&#8217;',' \'', text) #Transform apostrophes
    # text = re.sub(r'&#\d{2,4};', '', text) #Remove HTML Numbers
    text = re.sub(r'-', ' ', text) #Replace - by space
    text = re.sub(r'\d+', '', text) #Remove digits
    text = re.sub(r'[^\w\s\'’]','', text) #Remove punctuation without apostrophe
    text = re.sub(r'[\'’]', '\'', text) #Replace ’ by '
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

def createBackup(url_list, backup_file):
    pages_dict = {
        url_list[0]: getDivContent(downloadURL(url_list[0])),
        url_list[1]: getDivContent(downloadURL(url_list[1])),
        url_list[2]: getDivContent(downloadURL(url_list[2])),
        url_list[3]: getDivContent(downloadURL(url_list[3])),
        url_list[4]: getDivContent(downloadURL(url_list[4]))
    }
    pickleFile(backup_file, pages_dict)
    print("File", backup_file, "created.")
    return pages_dict

def main():
    url_list = readFile("url_list.txt")
    backup_file = 'downloaded_pages.backup'
    if not os.path.exists(backup_file):
        print("Backup file not existing, creating a new one.")
        pages_dict = createBackup(url_list, backup_file)
    else:
        print("Backup file existing, importing it.")
        pages_dict = unpickleFile(backup_file)

    #Cleaning Text and regroup it in one corpus
    corpus = []
    for url, content in pages_dict.items():
        print("Treating URL :", url)
        content = cleanText(content)
        pages_dict[url] = content
        for content_item in content:
            corpus.append(content_item)

    vec = CountVectorizer(min_df=5, max_df=0.9, ngram_range=(1, 2), token_pattern='(\S+)').fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0) 
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
    print(words_freq)

if __name__ == "__main__":
    main()
