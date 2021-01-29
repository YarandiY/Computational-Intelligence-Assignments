# -*- coding: utf-8 -*-
"""FinalProject (1).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uI_eNqKbbQPvRP3KEsfM7sP5LsZ4XtaU
"""

from google.colab import drive
drive.mount('/content/drive')

!sudo apt install python-pip
!sudo pip install hazm
!pip install tqdm

import pandas as pd
from hazm import *
import sklearn.model_selection
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
import re
import itertools
from sklearn.pipeline import Pipeline
import csv
from tqdm import tqdm_notebook as tqdm

from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics.pairwise import cosine_similarity
from sklearn import linear_model

train_url = 'drive/My Drive/train.csv'
test_url = 'drive/My Drive/test.csv'
result_url = "drive/My Drive/"
stopwords_url = 'drive/My Drive/stopwords.txt'

def save_result(results, name):
  f = open(result_url+name, "w")
  writer = csv.writer(f)
  writer.writerow(["Id", "Category"])
  for i in range(len(test_df)):
    writer.writerow([i, results[i]])
  f.close()

def read_data(url):
  df = pd.read_csv(url, engine='python',encoding='utf-8', error_bad_lines=False)
  df.head()
  return df

def stopwords():
  # stopwords = stopwords_list()
  text_file = open(stopwords_url, "r")
  sw = text_file.read().split('\n')
  return sw

print(stopwords())

"""# Data : train

 
"""

df = read_data(train_url)
x_train = df["Text"]
categories = np.array(list(set(df["Category"]))) 
y_train = df["Category"]
y_train_hot = pd.get_dummies(y_train)
print(len(y_train))
print(len(x_train))
print(y_train)
# x_train,x_validation,y_train,y_validation=sklearn.model_selection.train_test_split(x_train, y_train, test_size=0.15)

"""# Preprocessing

"""

def information(df):
  number_of_each_categories = {}
  for c in categories :
    index = df.index[df["Category"] == c].tolist()
    number_of_rows = len(index)
    number_of_each_categories[c] = number_of_rows
  max_value = sum(number_of_each_categories.values())/len(number_of_each_categories.values())
  for c in categories:
    if number_of_each_categories[c] >= max_value:
      continue
    tmp = df['Category'] == c
    indexes = df[tmp]
    n = max_value - number_of_each_categories[c]
    nn = int(n/len(indexes))
    df = df.append([indexes]*nn, ignore_index=True)
    nn = n - nn
    number_of_each_categories[c]+=n
    index = df.index[df["Category"] == c].tolist()
    number_of_rows = len(index)
  return df
      


df = information(df)

x_train = df["Text"]
categories = np.array(list(set(df["Category"]))) 
y_train = df["Category"]
y_train_hot = pd.get_dummies(y_train)
print(len(y_train))
print(len(x_train))
print(y_train)

normalizer = Normalizer()
stemmer = Stemmer()
lemmatizer = Lemmatizer()

def preprocessor(doc):
  norm = normalizer.normalize(doc)
  norm = re.sub("\d+", "", norm)
  norm = re.sub(r'\s*[A-Za-z]+\b', '' , norm)
  return norm

#Test
sample = x_train[0]
print(sample)
sample_pre = preprocessor(sample)
print(sample_pre)

"""# Tokenize the documents and remove stopwords
sw = stopwords and special characters

"""

sw = stopwords()
def tokenizer(doc):
  words = word_tokenize(doc)
  result = [] 
  for w in words:
    if w in sw :
      continue
    result.append(w)
  return result

#Test
sample_token = tokenizer(sample_pre)
print(sample_token)

"""# Extracting the features of each document"""

def get_features(input):
  features = [];
  for doc in tqdm(input):
    # doc = input[i]
    doc = preprocessor(doc)
    doc = tokenizer(doc)
    features.append(doc)
  return features

#Test
tmp = get_features(x_train[:6])

x = get_features(x_train)

x[0]

"""# Calculating tfidf"""

def get_data(doc):
  # doc = preprocessor(doc)
  # doc = tokenizer(doc)
  return doc

tfidf_vectorize = TfidfVectorizer(
    analyzer='word',
    tokenizer=get_data,
    preprocessor=get_data,
    token_pattern=None,
    min_df = 20
    )

train_tfidf = tfidf_vectorize.fit_transform(x)

"""# Preparing the tests"""

test_df = read_data(test_url)
x_test = test_df["Text"]

test = get_features(x_test)
test_tfidf = tfidf_vectorize.transform(test)

print(test[0])

"""# Selecting a model to classify

# Logistic Regression
"""

#models
logistic_regression = Pipeline([
                               ('clf', linear_model.LogisticRegression(n_jobs=1, C=1e5))
]);
# cosine_similarity = (train_tfidf * train_tfidf.T).A

model = logistic_regression.fit(train_tfidf, y_train)

results = model.predict(test_tfidf) 
save_result(results, "result.csv")

"""# LinearSVC"""

from sklearn.svm import LinearSVC
model2 = LinearSVC().fit(train_tfidf, y_train)

results2 = model2.predict(test_tfidf) 
save_result(results2, "result2.csv")

"""# MultinomialNB"""

model1 =  MultinomialNB().fit(train_tfidf, y_train);
results3 = model2.predict(test_tfidf) 
save_result(results3, "result3.csv")

