import pandas as pd
import os
import pickle
from parsing_sentences import parsing_sentences
from collections import OrderedDict

#function for printing data for debugging purposes and for storing the results to dictionaries
def update_data(event, key_begin, key_end, labels):
    for row in range(key_begin,key_end+1):
        print('For {0}: {1} in the paragraph {2} in the sentence {3}'.format(event, lemmas[row], paragraphs[row], sentences[row]))
    if labels[sentences[row]] == [None]:
        labels.update({sentences[row]:[event]})
        sent.append(sentences[row])
        parag.append(paragraphs[row])
        texts.append(sentences_text[row])
        label.append(event)
    else:
        labels[sentences[row]].append(event)

errors = []
directory = "Z:/Documents/event extraction/all_sentences/"
print(directory)
for filename in os.listdir(directory):
    name = directory + filename
    df = pd.read_csv(name, encoding='utf-8', sep=',')
    sent = []
    parag = []
    label = []
    texts = []

    #4 events with their most frequent structures and keywords stored in the dictionary 
    structures = {'avioliitto':[('solmia',{'avioliitto':'Case=Gen'}),('avioitua',),('mennä',{'naimisiin':''}),],
                  'kuolema':[('kuolla',),('hukkua',),('menehtyä',),('tehdä',{'itsemurha':'Case=Gen'}),],
                  'muuttaminen':[('muuttaa','PROPN Case=Ill'),('lähteä','PROPN Case=Ill'),('siirtyä','PROPN Case=Ill'),],
                  'tutkinnon suorittaminen':[('suorittaa',{'tutkinto':'Case=Gen'}),('valmistua','Case=Tra'),('tulla',{'maisteri':'Case=Tra'}),('päästä',{'maisteri':'Case=Tra'}),],
                 }
    
    #"parsing sentences" function adds 'sentenceText' column to df, so removing it causes KeyError and events won't be labelled
    #if the directory contains files with "sentenceText", it can be omitted
    #parsing_sentences(df, filename, lemma=True)
    
    df['tags_and_features'] = df['upos'] + " " + df['feat']
    data = df.to_dict()
    
    try:
        biographies = data['id'] #currently not used, but may be useful in the future
        lemmas = data['lemma']
        paragraphs = data['paragraph']
        features = data['feat']
        sentences = data['sentence']
        sentences_text = data['sentenceText']
        tags_and_features = data['tags_and_features']

        dicts = {'avioliitto':[], 'kuolema':[],'muuttaminen':[], 'tutkinnon suorittaminen':[]}

        labels = dict(zip(sentences.values(), [["NO_LABEL"]]*len(sentences)))

        #iterating over all lemmas
        for key, value in lemmas.items():
            #iterating over all structures
            for event, keywords in structures.items():
                for j in keywords:
                    #if it is verb + adverb/noun
                    if len(j) == 2:
                        if value == j[0]:
                            print(key)
                            key_begin = key_end = key
                            if type(j[1]) is dict:
                                print('is dict')
                                print(key_begin)
                                print(filename)
                                try:
                                    while sentences[key_begin] == sentences[key_end]:
                                        k = list(j[1].keys())[0]
                                        v = list(j[1].values())[0]

                                        #finding the end of the structure
                                        #true if v is an empty string in case there are no particular morphological features
                                        if lemmas[key_end] == k and v in str(tags_and_features[key_end]):
                                            update_data(event, key_begin, key_end, labels)
                                            break
                                        else:
                                            key_end += 1
                                except KeyError:
                                    continue
                            else:
                                if '=' in j[1]:
                                    print(j[1])
                                    try:
                                        while sentences[key_begin] == sentences[key_end]:
                                            if j[1] in str(tags_and_features[key_end]):
                                                update_data(event, key_begin, key_end, labels)
                                                break
                                            else:
                                                key_end += 1
                                    except KeyError:
                                        continue
                                else:
                                    if lemmas[key_end] == j[1]:
                                        update_data(event, key_begin, key_end, labels)
                                        break
                                    else:
                                        key_end += 1
                    #if the structure is a verb only
                    else:
                        if value == j[0]:
                            key_begin = key_end = key
                            update_data(event, key_begin, key_end, labels)

        try:
            df_results = pd.DataFrame({'Sentence': sent, "Sentence_Text": texts, 'Paragraph': parag, 'Label': label})
        except ValueError:
            errors.append(name)
        with open("Z:/Documents/event extraction/test/{}".format(filename), "w", encoding="utf-8") as r:
            df_results.to_csv(r, index=False)
    except KeyError:
        errors.append(name)
        print(name)
pickle.dump(errors, open("Z:/Documents/event extraction/errors.pickle", "ab+"))