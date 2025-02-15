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
    # print("Cleaning Text");
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
    # print("Text cleaned.");
    return (filtered_text);

def createBackup(url_list, backup_file):
    pages_dict = {};
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

def createWordClouds(words_dict):
    stopwords = set(STOPWORDS);
    for name, content in words_dict.items():
        filename = "./outputs/" + name + ".png"
        if not os.path.exists(filename):
            print("Creating a cloud of words for", name);
            wordcloud = WordCloud(width = 800, height = 800,
                                  background_color = 'white',
                                  stopwords = stopwords,
                                  min_font_size = 10).generate(content);
            wordcloud.to_file(filename);
            print("Cloud of words saved in file", filename);
        else:
            print("Cloud of words is already existing for", name);

def createUniqueWordCounter(words_dict):
    filename = "./outputs/UniqueWordsCount.png"
    print("Creating a unique word counter file.");
    names_list = [];
    counter = [];
    rgx = re.compile(r'(^\w+-\w+)');
    for name, content in words_dict.items():
        name = str(rgx.findall(name)[0]);
        names_list.append(name);
        counter.append(len(set(content.split())));
    # counter.sort(reverse=True);
    # names_list.sort(reverse=True);
    fig, ax = plt.subplots();
    ax.barh(names_list, counter, align='center');
    plt.title('Number of Unique Words');
    ax.set_yticks(names_list);
    ax.set_yticklabels(names_list);
    ax.invert_yaxis();  # labels read top-to-bottom
    plt.savefig(filename);
    print("Unique words counter saved in file", filename);

def createWordsPerMinute(words_dict):
    filename = "./outputs/WordsPerMinute.png"
    print("Creating a Words Per Minute file.");
    names_list = [];
    counter = [];
    rgx = re.compile(r'(^\w+-\w+)');
    for name, content in words_dict.items():
        name = str(rgx.findall(name)[0]);
        names_list.append(name);
        counter.append(len(content.split()) / 100);
    fig, ax = plt.subplots();
    ax.barh(names_list, counter, align='center');
    plt.title('Number of Words Per Minute');
    ax.set_yticks(names_list);
    ax.set_yticklabels(names_list);
    ax.invert_yaxis();  # labels read top-to-bottom
    plt.savefig(filename);
    print("Words Per Minute saved in file", filename);

def createBadWords(words_dict):
    filename = "./outputs/BadWords.png"
    print("Creating a bad words counter file.");
    names_list = [];
    f = [];
    s = [];
    rgx = re.compile(r'(^\w+-\w+)');
    for name, content in words_dict.items():
        name = str(rgx.findall(name)[0]);
        names_list.append(name);
        f.append(content.count("fuck") + content.count("fucking"));
        s.append(content.count("shit"));
    fig, ax = plt.subplots();
    plt.title('Number of Bad Words Used in Routine');
    plt.xlabel('Number of F Bombs');
    plt.ylabel('Number of S Words');
    # for url, cont in words_dict.items():
    #     plt.text(f, s, names_list);
    for i, name in enumerate(names_list):
        plt.text(f[i] + 2, s[i] + 1, name)
    # ax.grid(True);
    plt.scatter(f, s);
    plt.savefig(filename);
    print("Bad words counter saved in file", filename);

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
        print("Cleaning text for", url_name);
        content = cleanText(content);
        pages_dict[url] = content;
        for content_item in content:
            text_words += content_item + " "
        words_dict[url_name] = text_words;

    createWordClouds(words_dict);
    createUniqueWordCounter(words_dict);
    createWordsPerMinute(words_dict);
    createBadWords(words_dict);

if __name__ == "__main__":
    main();
