import pandas as pd
import os
import pickle
from parsing_sentences import parsing_sentences
from collections import OrderedDict

#function for printing data for debugging purposes and for storing the results to dictionaries
def update_data(event, key_begin, key_end, dicts, labels, s, p, l, t):
    for row in range(key_begin,key_end+1):
        print('For {0}: {1} in the paragraph {2} in the sentence {3}'.format(event, lemmas[row], paragraphs[row],sentences[row]))
    if labels[sentences[row]] == [None]:
        labels.update({sentences[row]:[event]})
        s.append(sentences[row])
        p.append(paragraphs[row])
        t.append(sentences_text[row])
        l.append(event)
    else:
        labels[sentences[row]].append(event)

def remove_none(dicts):
    clean_dict = dicts.copy()
    for key in dicts.keys():
        if dicts[key] == [None]:
            del clean_dict[key]
    return clean_dict

errors = []
directory = "Z:/Documents/event extraction/all_biographies/"
for filename in os.listdir(directory):
    name = directory + filename
    df = pd.read_csv(name, encoding='utf-8', sep=';')
    s = []
    p = []
    l = []
    t = []

    #4 events with their most frequent structures and keywords stored in the dictionary 
    structures = {'avioliitto':[('solmia',{'avioliitto':'Case=Gen'}),('avioitua',),('mennä',{'naimisiin':''}),],
                  'kuolema':[('kuolla',),('hukkua',),('menehtyä',),('tehdä',{'itsemurha':'Case=Gen'}),],
                  'muuttaminen':[('muuttaa','Case=Ill'),('lähteä','Case=Ill'),('siirtyä','Case=Ill'),],
                  'tutkinnon suorittaminen':[('suorittaa',{'tutkinto':'Case=Gen'}),('valmistua','Case=Tra'),('tulla',{'maisteri':'Case=Tra'}),('päästä',{'maisteri':'Case=Tra'}),],
                 }

    df.head()

    parsing_sentences(df, name, lemma=True)

    data = df.to_dict()
    try:
        biographies = data['id'] #currently not used, but may be useful in the future
        lemmas = data['lemma']
        paragraphs = data['paragraph']
        features = data['feat']
        sentences = data['sentence']
        sentences_text = data['sentenceText']

        dicts = {'avioliitto':[], 'kuolema':[],'muuttaminen':[], 'tutkinnon suorittaminen':[]}

        labels = dict(zip(sentences.values(), [[None]]*len(sentences)))

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
                                        if lemmas[key_end] == k and v in str(features[key_end]):
                                            update_data(event, key_begin, key_end, dicts, labels,s, p , l, t)
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
                                            if j[1] in str(features[key_end]):
                                                update_data(event, key_begin, key_end, dicts, labels, s, p, l, t)
                                                break
                                            else:
                                                key_end += 1
                                    except KeyError:
                                        continue
                                else:
                                    if lemmas[key_end] == j[1]:
                                        update_data(event, key_begin, key_end, dicts, labels,s, p, l, t)
                                        break
                                    else:
                                        key_end += 1
                    #if the structure is a verb only
                    else:
                        if value == j[0]:
                            key_begin = key_end = key
                            #print(key_begin)
                            print('not dict')
                            update_data(event, key_begin, key_end, dicts, labels, s, p, l, t)   

        clean_labels = remove_none(labels)
        results = pd.DataFrame({'label':list(clean_labels.values()),'sentence': list(clean_labels.keys())})
        #results_with_paragraphs = pd.DataFrame({'label':list(clean_labels.values()),'sentence': list(clean_labels.keys()), 'paragraph':})
        results.label.value_counts()

        test_labels = pd.read_csv('test_data_labels.csv', encoding='utf-8', sep=';')
        #print(test_labels.label.value_counts())

        results_dict = results.to_dict()
        #n = list(results_dict['label'].values()).index(['tutkinnon suorittaminen', 'muuttaminen', 'tutkinnon suorittaminen', 'muuttaminen'])
        # n = list(results_dict['label'].values()).index(['muuttaminen','muuttaminen'])
        # sent = results_dict['sentence'][n]
        # parag = sent.split('#')[0]
        # print(n)
        # print('Sentence {0} in paragraph {1}'.format(sent, parag))
        # print(list(results_dict['label'].values()))

        # sen_l = list(sentences.values()).index(sent)
        # df.loc[sen_l,]

        # df.paragraphText.loc[sen_l,]

        test_labels_dict = test_labels.to_dict()
        right_labels = dict(zip(list(test_labels_dict['sentence'].values()), [[i] for i in list(test_labels_dict['label'].values())]))

        final_labels = dict(zip(list(results_dict['sentence'].values()), list(results_dict['label'].values())))
        #len(final_labels)

        result_list = []
        for k in right_labels.keys():
            try:
                #we are also taking into account partially correct labels
                if right_labels[k] == final_labels[k] or right_labels[k][0] in final_labels[k]:
                    result_list.append((True,'true label'))
                else:
                    result_list.append((False, 'false label'))
            except KeyError:
                result_list.append((False, 'not in results'))
        #print(sum(result_list)/len(result_list))
        #len(result_list)
        result_list1 = [i[0] for i in result_list]
        #print(sum(result_list1))

        x = [i[1] for i in result_list if i[1] == 'true label']

        new_labels = []
        i = 0
        for k in final_labels.keys():
            try:
                if right_labels[k]:
                    i += 1
            except KeyError:
                new_labels.append((k, final_labels[k]))

        try:
            df_results = pd.DataFrame({'Sentence': s, "Sentence_Text": t, 'Paragraph': p, 'Label': l})
        except ValueError:
            errors.append(name)
            print(errors)
        with open("Z:/Documents/event extraction/all_results/{}".format(filename), "w", encoding="utf-8") as r:
            df_results.to_csv(r, index=False)
    except KeyError:
        errors.append(name)
        print(errors)
pickle.dump(errors, open("Z:/Documents/event extraction/errors.pickle", "ab+"))