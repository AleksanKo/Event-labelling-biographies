import pandas as pd
from collections import OrderedDict
import os
import pickle

def parsing_sentences(df, name, lemma=False):

    sentence = list(df["sentence"])
    lemmas = list(df["lemma"]) #for now sentences are parsed only for original forms
    original_forms = list(df["originalForm"])
    words_ids = list(df["wordOrderNumber"])
    
    if lemma:
        forms = lemmas
    else:
        forms = original_forms

    #iterate while id != 1, if the next id == 1 - break, if KeyError - break
    #problem: due to parsing issues of the data, some sentences begin with id == 2

    end = len(words_ids)
    whole_sentences = []
    whole_sentence = ""
    curr = 0
    while curr < end:
        if words_ids[curr] == 1:
            whole_sentence += forms[curr] + " "
            curr += 1
        else:
            try:
                while words_ids[curr] != 1:
                    whole_sentence += forms[curr] + " "
                    curr += 1
            except IndexError:
                whole_sentences.append(whole_sentence)
                break
            whole_sentences.append(whole_sentence)
            whole_sentence = ""
    whole_sentences.append(whole_sentence)

    whole_sentences = [i.strip() for i in whole_sentences]
    whole_sentences = [i.replace("&quot;","\"") for i in whole_sentences]
    whole_sentences = [i.replace("&amp;","&") for i in whole_sentences]
    
    #OrderedDict is required because id for titles begins with "t", so after sorting it is placed at the end of the list
    sentences_with_headers = list(OrderedDict.fromkeys(sentence))
    sent_text = dict(zip(sentences_with_headers, whole_sentences))

    all_sentences = []

    for i in sentence:
        try:
            all_sentences.append(sent_text[i])
        except KeyError:
            continue
    try:
        df['sentenceText'] = all_sentences
        with open("Z:/Documents/event extraction/all_sentences_lemmatized/{}".format(name), "w", encoding="utf-8") as r:
            df.to_csv(r, index=False, header=True)
    except ValueError:
        df_err = pd.DataFrame({"Name": name}, index=[0])
        with open("Z:/Documents/event extraction/errors.csv", "a", encoding="utf-8") as f:
            df_err.to_csv(f, header=False, index=False)

if __name__ == "__main__":
    directory = "Z:/Documents/event extraction/all_biographies/"
    for filename in os.listdir(directory):
        name = directory + filename
        df = pd.read_csv(name, encoding='utf-8', sep=';')
        parsing_sentences(df, filename, lemma=True)