import sys
import nltk
import pandas as pd
import numpy as np
import re
import collections

from common.download_utils import download_week1_resources
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from ast import literal_eval
from collections import Counter
from scipy import sparse as sp_sparse

sys.path.append("..")
download_week1_resources()

nltk.download('stopwords')
nltk.download('punkt')

def read_data(filename):
    data = pd.read_csv(filename, sep='\t')
    data['tags'] = data['tags'].apply(literal_eval)
    return data

train = read_data('data/train.tsv')
validation = read_data('data/validation.tsv')
test = pd.read_csv('data/test.tsv', sep='\t')

train.head()

X_train, y_train = train['title'].values, train['tags'].values
X_val, y_val = validation['title'].values, validation['tags'].values
X_test = test['title'].values

REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
STOPWORDS = set(stopwords.words('english'))

def text_prepare(text):
    """
        text: a string
        return: modified initial string
    """
    text = text.lower() # lowercase text
    text = re.sub(REPLACE_BY_SPACE_RE, ' ', text) # replace REPLACE_BY_SPACE_RE symbols by space in text
    text = re.sub(BAD_SYMBOLS_RE, '', text) # delete symbols which are in BAD_SYMBOLS_RE from text

    # delete stopwords from text
    filtered_text = ""
    tokenized_text = word_tokenize(text)
    for i in range(len(tokenized_text)):
        if not tokenized_text[i] in STOPWORDS:
            filtered_text += tokenized_text[i];
            if i != len(tokenized_text) - 1:
                filtered_text += ' '

    return filtered_text

def test_text_prepare():
    examples = ["SQL Server - any equivalent of Excel's CHOOSE function?",
                "How to free c++ memory vector<int> * arr?"]
    answers = ["sql server equivalent excels choose function",
               "free c++ memory vectorint arr"]
    for ex, ans in zip(examples, answers):
        if text_prepare(ex) != ans:
            return "Wrong answer for the case: '%s'" % ex
    return 'Basic tests are passed.'

print(test_text_prepare())

prepared_questions = []

for line in open('data/text_prepare_tests.tsv', encoding='utf-8'):
    line = text_prepare(line.strip())
    prepared_questions.append(line)

text_prepare_results = '\n'.join(prepared_questions)
# grader.submit_tag('TextPrepare', text_prepare_results)

X_train = [text_prepare(x) for x in X_train]
X_val = [text_prepare(x) for x in X_val]
X_test = [text_prepare(x) for x in X_test]


# Dictionary of all words from train corpus with their counts.
print("Counting words and tags :")
words_counts = {}
tags_counts = {}

words=[]
tags=[]
for i in range(0, len(X_train)):
    if i % 1000 == 0 :
        print(((i / 1000) + 1), "%")
    words = words + (re.findall(r'\w+', X_train[i])) # cantain all the words in the dataset
    tags = tags + y_train[i] # contain tags present in the dataset
print("Finished")

words_counts = Counter(words) # Create word map of occurences
tags_counts=Counter(tags) # Create tags map of occurences

most_common_tags = sorted(tags_counts.items(), key=lambda x: x[1], reverse=True)[:3]
most_common_words = sorted(words_counts.items(), key=lambda x: x[1], reverse=True)[:3]

print('Most common Tags:', '%s\nMost common Words: %s' % (','.join(tag for tag, _ in most_common_tags), ','.join(word for word, _ in most_common_words)))


DICT_SIZE = 5000
WORDS_TO_INDEX = {}
INDEX_TO_WORDS = {}

most_common_words = sorted(words_counts.items(), key=lambda x: x[1], reverse=True)[:5000]
for i in range(0, DICT_SIZE):
    WORDS_TO_INDEX[most_common_words[i][0]] = i
    INDEX_TO_WORDS[i] = most_common_words[i][0]


def my_bag_of_words(text, words_to_index, dict_size):
    """
        text: a string
        dict_size: size of the dictionary

        return a vector which is a bag-of-words representation of 'text'
    """
    result_vector = np.zeros(dict_size)
    words = text.split(" ")
    for i in range(0, len(words)):
        for key, value in words_to_index.items():
            if words[i] == key :
                result_vector[words_to_index[key]] += 1
    return result_vector

def test_my_bag_of_words():
    words_to_index = {'hi': 0, 'you': 1, 'me': 2, 'are': 3}
    examples = ['hi how are you']
    answers = [[1, 1, 0, 1]]
    for ex, ans in zip(examples, answers):
        if (my_bag_of_words(ex, words_to_index, 4) != ans).any():
            return "Wrong answer for the case: '%s'" % ex
        return 'Basic tests are passed.'

print(test_my_bag_of_words())

X_train_mybag = sp_sparse.vstack([sp_sparse.csr_matrix(my_bag_of_words(text, WORDS_TO_INDEX, DICT_SIZE)) for text in X_train])
X_val_mybag = sp_sparse.vstack([sp_sparse.csr_matrix(my_bag_of_words(text, WORDS_TO_INDEX, DICT_SIZE)) for text in X_val])
X_test_mybag = sp_sparse.vstack([sp_sparse.csr_matrix(my_bag_of_words(text, WORDS_TO_INDEX, DICT_SIZE)) for text in X_test])

print('X_train shape ', X_train_mybag.shape)
print('X_val shape ', X_val_mybag.shape)
print('X_test shape ', X_test_mybag.shape)

row = X_train_mybag[10].toarray()[0]

non_zero_elements_count = 0
for i in range(0, DICT_SIZE):
    if (row[i] == 1):
        non_zero_elements_count += 1

print('BagOfWords : ', non_zero_elements_count)
