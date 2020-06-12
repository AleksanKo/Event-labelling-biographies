import pandas as pd
from pprint import pprint
from collections import OrderedDict
import os

def parsing_sentences(df, errors, name):

    sentence = list(df["sentence"])
    lemmas = list(df["lemma"]) #for now sentences are parsed only for original forms
    original_forms = list(df["originalForm"])
    words_ids = list(df["wordOrderNumber"])
    #iterate while they are consecutive, if the next is 1 - break, if KeyError - break

    end = len(words_ids)
    whole_sentences = []
    whole_sentence = ""
    curr = 0
    while curr < end:
        if words_ids[curr] == 1:
            whole_sentence += original_forms[curr] + " "
            curr += 1
        else:
            try:
                while words_ids[curr] != 1:
                    whole_sentence += original_forms[curr] + " "
                    curr += 1
                    print(whole_sentence)
                    print(curr)
            except IndexError:
                whole_sentences.append(whole_sentence)
                #print("break!" + whole_sentence)
                break
            whole_sentences.append(whole_sentence)
            whole_sentence = ""
    whole_sentences.append(whole_sentence)
    #pprint(whole_sentences)
    #print(whole_sentence)
    #print(len(whole_sentences))
    #print(set(sentence))
    whole_sentences = [i.strip() for i in whole_sentences]
    whole_sentences = [i.replace("&quot;","\"") for i in whole_sentences]
    whole_sentences = [i.replace("&amp;","&") for i in whole_sentences]
    
    #because id for titles begins with "t", so after sorting it is placed at the end of the list
    #sentences_with_headers = [sorted(list(set(sentence)))[-1]] + sorted(list(set(sentence)))[:-1]
    #либо втупую удалять дубликаты из списка, пока они есть
    sentences_with_headers = list(OrderedDict.fromkeys(sentence))
    sent_text = dict(zip(sentences_with_headers, whole_sentences))

    all_sentences = []

    for i in sentence:
        try:
            all_sentences.append(sent_text[i])
        except KeyError:
            #print(i)
            continue
    
    #print(len(all_sentences))
    #print(len(whole_sentences))
    #print(len(sentences_with_headers))
    #print(len(sentence))
    try:
        df['sentenceText'] = all_sentences
        with open("Z:/Documents/event extraction/all_sentences/{}".format(name), "w", encoding="utf-8") as r:
            df.to_csv(r, index = False, header=True)
    except ValueError:
        errors.append(name)
        print(errors)
    #print(sentences_with_headers)
    print(len(whole_sentences))
    #hole_sentences = whole_sentences + ['']
    #df_result = pd.DataFrame({'S':sentences_with_headers, 'L': hole_sentences})
    #df_result.to_csv("new.csv")
    print(sent_text)

#df = pd.read_csv("Z:/Documents/event extraction/all_biographies/p10000.csv", encoding='utf-8', sep=';')
#parsing_sentences(df, [], "p10000.csv")

if __name__ == "__main__":
    directory = "Z:/Documents/event extraction/all_biographies/"
    for filename in os.listdir(directory):
        name = directory + filename
        df = pd.read_csv(name, encoding='utf-8', sep=';')
        parsing_sentences(df, [], filename)



#check the errors and think how to improve scripts for them regarding problems
