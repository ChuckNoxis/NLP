#!/usr/local/bin/python3
## Assignment4
##

import re
import nltk
import requests
import pickle
import os.path
import sklearn
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud, STOPWORDS

# nltk.download('stopwords')

def readFile(filename):
    f = open(filename, "r");
    data = [];
    for line in f.readlines():
        line = re.sub(r'[\n]', '', line);
        data.append(line);
    return (data);

def downloadURL(url):
    print('Downloading page :', url);
    res = requests.get(url);
    if res.status_code == 200:
        print('Download Success!');
    elif res.status_code == 404:
        print('Error 404 with URL ', url, ' : Not Found.');
    else:
        print('Error ', res.status_code, 'on URL : ', url);
    return (res.content);

def pickleFile(filename, pages_dict):
    print("Pickling File");
    f = open(filename, 'wb');
    pickle.dump(pages_dict, f);
    f.close();
    print("File pickled");

def unpickleFile(filename):
    print("Unpickling File");
    f = open(filename, 'rb');
    new_dict = pickle.load(f);
    f.close();
    print("File unpickled");
    return (new_dict);

def getDivContent(page):
    soup = BeautifulSoup(page, 'html.parser');
    post_content = soup.find(class_="post-content").find_all('p');
    post_content = ' '.join(map(str, post_content));
    return (post_content);

def cleanText(text):
    print("Cleaning Text");
    text = text.lower(); #Lowercase Text
    text = re.sub(r'<\/?[\w ="-:;]*>', '', text); #Remove HTML Tags
    text = re.sub(r'-', ' ', text); #Replace - by space
    text = re.sub(r'\d+', '', text); #Remove digits
    text = re.sub(r'[^\w\s]', '', text); #Remove punctuation
    text = re.sub(r'[\n]', ' ', text); #Replace \n by space
    text = re.sub(r'[\t]', '', text); #Remove \t

    tokenized_text = word_tokenize(text); #Tokenizetext

    filtered_text = [];
    stop_words = set(stopwords.words('english'));
    #Remove stopwords
    for i in range(len(tokenized_text)):
        if not tokenized_text[i] in stop_words:
            filtered_text.append(tokenized_text[i]);
    print("Text cleaned.");
    return (filtered_text);

def createBackup(url_list, backup_file):
    for url in url_list:
        pages_dict[url] = getDivContent(downloadURL(url));
    pickleFile(backup_file, pages_dict);
    print("File", backup_file, "created.");
    return (pages_dict);

def checkUrlList(url_list, pages_dict, backup_file):
    changed = False;
    for url in url_list:
        if url not in pages_dict.keys():
            print("URL", url, "is not in the backup file.");
            pages_dict[url] = getDivContent(downloadURL(url));
            changed = True;
        else:
            print("URL", url, "is already in the backup file.");
    if changed:
        pickleFile(backup_file, pages_dict);
    return (pages_dict);

def getUrlName(url):
    rgx = re.search('https?:\/\/scrapsfromtheloft\.com\/\d{4}\/(\d{2}\/){2}([\w\-]*)\/', url);
    return (rgx.group(2));

def createWordCloud(content, filename):
    print("Creating a Cloud of words for url :", filename);
    stopwords = set(STOPWORDS);
    filename = "./outputs/" + filename + ".png"
    wordcloud = WordCloud(width = 800, height = 800,
                background_color = 'white',
                stopwords = stopwords,
                min_font_size = 10).generate(content);
    wordcloud.to_file(filename);
    print("Cloud of words saved in file", filename);

def main():
    url_list = readFile("url_list.txt");
    backup_file = 'downloaded_pages.backup';
    if not os.path.exists(backup_file):
        print("Backup file not existing, creating a new one.");
        pages_dict = createBackup(url_list, backup_file);
    else:
        print("Backup file existing, importing it.");
        pages_dict = unpickleFile(backup_file);
        pages_dict = checkUrlList(url_list, pages_dict, backup_file);

    words_dict = {};
    #Cleaning Text
    for url, content in pages_dict.items():
        text_words = "";
        url_name = getUrlName(url);
        print("Treating page :", url_name);
        content = cleanText(content);
        pages_dict[url] = content;
        for content_item in content:
            text_words += content_item + " "
        words_dict[url_name] = text_words;

    for name, content in words_dict.items():
        if not os.path.exists("./outputs/" + name + ".png"):
            createWordCloud(content, name);
        else:
            print("Cloud of words is already existing.");
        print("Single world counter in", name);
        print(len(set(content.split())));
        # print(len())

if __name__ == "__main__":
    main();
