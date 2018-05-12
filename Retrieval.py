import math
import enchant
from elasticsearch import Elasticsearch
import re
import itertools, nltk, string, gensim
import pickle
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
import json
from itertools import takewhile, tee
import networkx
from nltk.corpus import wordnet as wn

def load_obj(name):
    with open('df/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def lambda_unpack(f):
    return lambda args: f(*args)

def tfidf(tf,df, N):
    idf = math.log(N/df)
    ti = tf * idf
    return ti


def baseline(terms,sec):
    with open('st/englishST.txt') as f:
        stop = f.read()
    with open('st/'+sec+'ST.txt') as f:
        fstop = f.read()
    stop_set = set()
    for x in stop.split('\n'):
        stop_set.add(x.strip())
    for y in fstop.split('\n'):
        stop_set.add(y.strip())

    rtStr = ''
    i=0

    for term in terms:
        tmp = re.sub('[!.,?/]', ' ', term)
        if len(tmp) > 2 and (not tmp.isdigit()) and (tmp not in stop_set) and i<1000:
            rtStr += tmp + ' '
            i +=1
    return rtStr

def termSelection(terms, N, sec, threshold):
    #d = enchant.Dict("en_US")
    with open('st/englishST.txt') as f:
        stop = f.read()
    with open('st/'+sec+'ST.txt') as f:
        fstop = f.read()
    stop_set = set()
    for x in stop.split('\n'):
        stop_set.add(x.strip())
    for y in fstop.split('\n'):
        stop_set.add(y.strip())


    vecMap = load_obj(sec[0:3]+'DF')

    term_map = {}
    for term in terms:
        tmp = re.sub('[!.,?]', '', term)

        if len(tmp) > 2 and (not tmp.isdigit()) and (tmp not in stop_set):  #and d.check(tmp)
            prop = terms[term]
            #df = prop["doc_freq"]
            if tmp in vecMap.keys():
                df = vecMap[tmp]
            else:
                df=1
            tf = prop["term_freq"]
            ti = tfidf(tf, df, N)

            term_map[tmp] = ti

    tmp = sorted(term_map.items(), key=lambda x:x[1], reverse=True)
    rt = {}
    i = 0
    size = min(1000, len(term_map)*threshold)
    for k, v in tmp:
        if i < size:
            rt[k] = v
        i=i+1

    rtstr = ' '.join(list(rt.keys()))
    return rtstr

def extract_chunks(text, grammar=r'KT: {(<JJ>* <NN.*>+ <IN>)? <JJ>* <NN.*>+}'):
    #lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()

    # exclude candidates that are stop words or entirely punctuation
    punct = set(string.punctuation)
    stop_words = set(nltk.corpus.stopwords.words('english'))
    # tokenize, POS-tag, and chunk using regular expressions
    chunker = nltk.chunk.regexp.RegexpParser(grammar)
    tagged_sents = nltk.pos_tag_sents(nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(text))
    all_chunks = list(itertools.chain.from_iterable(nltk.chunk.tree2conlltags(chunker.parse(tagged_sent))
                                                    for tagged_sent in tagged_sents))
    # join constituent chunk words into a single chunked phrase
    candidates = [' '.join(stemmer.stem(word) for word, pos, chunk in group).lower()
                  for key, group in
                  itertools.groupby(all_chunks, lambda_unpack(lambda word, pos, chunk: chunk != 'O')) if key]

    return list(set([cand for cand in candidates
            if cand not in stop_words and not all(char in punct for char in cand)]))

def phraseSelection(chunks, terms, N, sec, threshold):
    #lemmatizer = WordNetLemmatizer()
    #stemmer = PorterStemmer()
    with open('st/englishST.txt') as f:
        stop = f.read()
    with open('st/'+sec+'ST.txt') as f:
        fstop = f.read()
    stop_set = set()
    for x in stop.split('\n'):
        stop_set.add(x.strip())
    for y in fstop.split('\n'):
        stop_set.add(y.strip())

    phrase_map = {}
    phrase_str = ""
    br = False
    for ck in chunks:
        mean=0
        l = ck.split(' ')
        if len(l)>3:
            continue
        for ll in l:
            #t = lemmatizer.lemmatize(ll)
            #ll = stemmer.stem(ll)
            if len(ll)<4 and ll in stop_set:
                br = True
                break
            if ll in terms.keys():
                prop = terms[ll]
                df = prop["doc_freq"]
                tf = prop["term_freq"]
                ti = tfidf(tf, df, N)
                mean += ti
        if not br:
            mean /= len(l)
            phrase_map[ck]=mean
        else:
            br = False

    tmp = sorted(phrase_map.items(), key=lambda x: x[1], reverse=True)
    rt = {}
    i = 0
    size = int(min(len(phrase_map) * threshold, 1000))
    print("size:",size)
    for k, v in tmp:
        k = re.sub('[!.,?]', ' ', k)
        if i < size:
            rt[k] = v
            phrase_str += "\""+k+"\""+" OR "
        i = i + 1

    phrase_str = phrase_str[0:-3]

    return phrase_str



def initQFormulate(es, qrel, N):
    patent_document = qrel["_source"]["patent-document"]

    #title
    title_str = ''
    title_phrase = ''
    title = patent_document["title"]
    if title != "":
        #print(title)
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent-document.title"])
        terms = rt["term_vectors"]["patent-document.title"]["terms"]
        #print(terms)
        ## baseline
        #title_str = baseline(terms, 'title')
        ## terms extraction
        #title_str = termSelection(terms, N, 'title', 1)
        ## phrase extraction
        chunks = extract_chunks(title)
        title_phrase = phraseSelection(chunks,terms,N,'title',1)

        #print(title_str)
        print(title_phrase)

    #abstract
    abstract_str=''
    abstract_phrase = ''
    abstract = patent_document["abstract"]
    if abstract != "":
        #print(abstract)
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent-document.abstract"])
        terms = rt["term_vectors"]["patent-document.abstract"]["terms"]
        #print(terms)
        ## baseline
        #abstract_str = baseline(terms, 'abstract')
        ## terms extraction
        #abstract_str = termSelection(terms, N, 'abstract', 1)
        ## phrase extraction
        chunks = extract_chunks(abstract)
        abstract_phrase = phraseSelection(chunks, terms, N, 'abstract', 1)

        #print(abstract_str)
        print(abstract_phrase)

    #print("description:")
    #description
    description_str=''
    description_phrase = ''
    desciption = patent_document["description"]
    if desciption != "":
        #print(desciption)
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent-document.description"])
        terms = rt["term_vectors"]["patent-document.description"]["terms"]
        ## baseline
        #description_str = baseline(terms, 'description')
        ## terms extraction
        #description_str = termSelection(terms, N, 'description', 1)
        ## phrase extraction
        chunks = extract_chunks(desciption)
        description_phrase = phraseSelection(chunks, terms, N, 'description', 0.9)

        #print(description_str)
        print(description_phrase)

    #print("claims:")
    #claims
    claims_str=''
    claims_phrase = ''
    claims = patent_document["claims"]
    if claims != "":
        #print(claims)
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent-document.claims"])
        terms = rt["term_vectors"]["patent-document.claims"]["terms"]
        ## baseline
        #claims_str = baseline(terms, 'claims')
        ## terms extraction
        #claims_str = termSelection(terms, N, 'claims', 1)
        ## phrase extraction
        chunks = extract_chunks(claims)
        claims_phrase = phraseSelection(chunks, terms, N, 'claims', 0.8)
        #print(claims_str)
        print(claims_phrase)


    #print("IPCR:")
    #IPCR
    ipcr = patent_document["ipcr"]
    ipcr_l1 = set()
    ipcr_l2 = []
    ipcr_l3 = []
    for ip in ipcr:
        ipcr_l1.add(ip.split()[0])
        ipcr_l2.append(ip.split()[0]+' '+ip.split()[1].split('/')[0])
        ipcr_l3.append(ip.split()[0]+' '+ip.split()[1])

    ipcr_str = ' '.join(list(ipcr_l1))
    print(ipcr_str)

    InitQ = {"title": title_str, "abstract": abstract_str, "description": description_str, "claims": claims_str, "ipcr": ipcr_str}
    InitQP = {"title": title_phrase, "abstract": abstract_phrase, "description": description_phrase, "claims": claims_phrase, "ipcr": ipcr_str}

    #print(InitQ)
    return InitQ, InitQP


def ReQFormulate(qrel):
    pass


def retrieve(es, qrel, qrelP):
    #synonym_graph token filter
    #print(' '.join(qrel["title"]))
    '''
    query = {
        "size": 100,
        "query": {
            "bool":{
                "should": [
                    {"query_string": {
                        "fields": ["patent-document.title^5",
                                   "patent-document.abstract^3", "patent-document.description",
                                   "patent-document.claims"],
                        "query": qrel["title"]
                    }
                    },

                    {"query_string": {
                        "fields": ["patent-document.abstract^3", "patent-document.description",
                                   "patent-document.claims"],
                        "query": qrel["abstract"]
                    }
                    },

                    {"query_string": {
                        "fields": ["patent-document.description"],
                        "query": qrel["description"]
                    }
                    },

                    {"query_string": {
                        "fields": ["patent-document.claims"],
                        "query": qrel["claims"]
                    }
                    },

                    {"query_string": {
                        "fields": ["patent-document.ipcr"],
                        "query": qrel["ipcr"]
                    }
                    }

                ]
                ,
                "minimum_should_match": 1,
                "boost": 1.0

            },
        }
    }
    '''

    query_prase = {
        "size": 100,
        "query": {
            "bool":{
                "must": [
                    {"query_string": {
                        "fields": ["patent-document.title",
                                   "patent-document.abstract", "patent-document.description",
                                   "patent-document.claims"],
                        "query": qrelP["title"]
                    }
                    },

                    {"query_string": {
                        "fields": ["patent-document.title",
                                   "patent-document.abstract", "patent-document.description",
                                   "patent-document.claims"],
                        "query": qrelP["abstract"]
                    }
                    },

                    {"query_string": {
                        "fields": ["patent-document.title",
                                   "patent-document.abstract", "patent-document.description",
                                   "patent-document.claims"],
                        "query": qrelP["description"]
                    }
                    },

                    {"query_string": {
                        "fields": ["patent-document.title",
                                   "patent-document.abstract", "patent-document.description",
                                   "patent-document.claims"],
                        "query": qrelP["claims"]
                    }
                    },

                    {"query_string": {
                        "fields": ["patent-document.ipcr"],
                        "query": qrelP["ipcr"]
                    }
                    }

                ]
            },
        }

    }

    query = {
        "size": 100,
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "patent-document.ipcr": qrel["ipcr"]
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.title^3", "patent-document.abstract^2",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrel["title"],
                            "tie_breaker": 0.5
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.title^3", "patent-document.abstract^3",
                                       "patent-document.description^2", "patent-document.claims"],
                            "query": qrel["abstract"],
                            "tie_breaker": 0.3
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract^2",
                                       "patent-document.description^2", "patent-document.claims"],
                            "query": qrel["description"],
                            "tie_breaker": 0.3
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims^3"],
                            "query": qrel["claims"],
                            "tie_breaker": 0.3
                        }
                    }

                ],
                "minimum_should_match": 3
            }

        }
    }


    query1 = {
        "size": 100,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrel["title"],
                            "tie_breaker": 0.3,
                            "type": "most_fields"
                        }
                    }
                ],
                "filter":[
                    {
                        "match": {
                            "patent-document.ipcr": qrel["ipcr"]
                        }
                    }
                ]
            }

        }
    }

    query2 = {
        "size": 100,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrel["abstract"],
                            "tie_breaker": 0.3,
                            "type": "most_fields"
                        }
                    }
                ],
                "filter":[
                    {
                        "match": {
                            "patent-document.ipcr": qrel["ipcr"]
                        }
                    }
                ]
            }
        }
    }

    query3 = {
        "size": 100,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrel["description"],
                            "tie_breaker": 0.3,
                            "type": "most_fields"
                        }
                    }
                ],
                "filter": [
                    {
                        "match": {
                            "patent-document.ipcr": qrel["ipcr"]
                        }
                    }
                ]
            }
        }
    }

    query4 = {
        "size": 100,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrel["claims"],
                            "tie_breaker": 0.3
                        }
                    }
                ],
                "filter": [
                    {
                        "match": {
                            "patent-document.ipcr": qrel["ipcr"]
                        }
                    }
                ]
            }

        }
    }

    query_comb = {
        "size": 100,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrel["title"],
                            "tie_breaker": 0.3
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrel["abstract"],
                            "tie_breaker": 0.3
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrel["description"],
                            "tie_breaker": 0.3
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrel["claims"],
                            "tie_breaker": 0.3
                        }
                    }
                ],
                "filter": [
                    {
                        "match": {
                            "patent-document.ipcr": qrel["ipcr"]
                        }
                    }
                ]
            }

        }

    }




    rs = es.search(index="patent", doc_type="patent", body=query_prase, timeout='60s', request_timeout=60)
    print(rs["hits"]["total"])
    return rs


def result(qrel, rs):
    hits = rs['hits']['hits']
    i = min(rs["hits"]["total"], 100)
    with open("/Users/linhonggu/Desktop/result.txt",'a') as file:
        for hit in hits:
            if i > 0:
                ucid = hit['_source']['patent-document']['ucid']
                file.write(qrel['_source']['patent-document']['PAC'] + " 0 " + ucid + " 1\n")
            i = i - 1


def main():
    '''
    for qrel in qrels:
        InitQFormulate(qrel)
        retrieve()
        ReQFormulate()
        retrieve()
        result()
    '''

    es = Elasticsearch(['http://localhost:9200/'])
    doc = {
        'size': 1351,
        'query': {
            'match_all': {}
        }
    }
    res = es.search(index='qrel', doc_type='patent', body=doc)

    N = 10469

    for qrel in res["hits"]["hits"]:
        iq, iqp = initQFormulate(es,qrel,N)
        rs = retrieve(es, iq, iqp)
        result(qrel, rs)


if __name__ == "__main__":
    main()