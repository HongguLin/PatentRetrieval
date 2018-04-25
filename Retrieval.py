import math
import enchant
from elasticsearch import Elasticsearch
import re
import itertools, nltk, string, gensim
import pickle
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

def getTermMap(terms, N, sec, threshold):
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

        if len(tmp) > 1 and (not tmp.isdigit()) and (tmp not in stop_set):  #and d.check(tmp)
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
    size = len(term_map)*threshold
    for k, v in tmp:
        if i < size:
            rt[k] = v
        i=i+1
    return rt

def extract_chunks(text, grammar=r'KT: {(<JJ>* <NN.*>+ <IN>)? <JJ>* <NN.*>+}'):
    #lemmatizer = WordNetLemmatizer()
    # exclude candidates that are stop words or entirely punctuation
    punct = set(string.punctuation)
    stop_words = set(nltk.corpus.stopwords.words('english'))
    # tokenize, POS-tag, and chunk using regular expressions
    chunker = nltk.chunk.regexp.RegexpParser(grammar)
    tagged_sents = nltk.pos_tag_sents(nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(text))
    all_chunks = list(itertools.chain.from_iterable(nltk.chunk.tree2conlltags(chunker.parse(tagged_sent))
                                                    for tagged_sent in tagged_sents))
    # join constituent chunk words into a single chunked phrase
    candidates = [' '.join(word for word, pos, chunk in group).lower()
                  for key, group in
                  itertools.groupby(all_chunks, lambda_unpack(lambda word, pos, chunk: chunk != 'O')) if key]

    return [cand for cand in candidates
            if cand not in stop_words and not all(char in punct for char in cand)]

def getChunkMap(chunks, terms, N, threshold):
    #lemmatizer = WordNetLemmatizer()
    phrase_map = {}
    for ck in chunks:
        mean=0
        l = ck.split(' ')
        if len(l)>3:
            continue
        for ll in l:
            #t = lemmatizer.lemmatize(ll)
            if ll in terms.keys():
                prop = terms[ll]
                df = prop["doc_freq"]
                tf = prop["term_freq"]
                ti = tfidf(tf, df, N)
                mean += ti
        mean /= len(l)
        phrase_map[ck]=mean

    tmp = sorted(phrase_map.items(), key=lambda x: x[1], reverse=True)
    rt = {}
    i = 0
    size = len(phrase_map) * threshold
    for k, v in tmp:
        if i < size:
            rt[k] = v
        i = i + 1
    return rt

def assignWeight():
    pass

def initQFormulate(es, qrel, N):
    patent_document = qrel["_source"]["patent-document"]

    #print("title:")
    #title
    title_map={}
    #title_chunk_map={}
    title = patent_document["title"]
    if title != "":
        #print(title)
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent-document.title"])
        terms = rt["term_vectors"]["patent-document.title"]["terms"]
        ## terms extraction
        title_map = getTermMap(terms, N, 'title', 1)
        ## phrase extraction
        #chunks = extract_chunks(title)
        #title_chunk_map = getChunkMap(chunks,terms,N,0.8)

        print(title_map)
        #print(title_chunk_map)

    #print("abstract:")
    #abstract
    abstract_map={}
    #abstract_chunk_map={}
    abstract = patent_document["abstract"]
    if abstract != "":
        #print(abstract)
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent-document.abstract"])
        terms = rt["term_vectors"]["patent-document.abstract"]["terms"]
        ## terms extraction
        abstract_map = getTermMap(terms, N, 'abstract', 1)
        ## phrase extraction
        #chunks = extract_chunks(abstract)
        #abstract_chunk_map = getChunkMap(chunks, terms, N, 0.7)

        print(abstract_map)
        #print(abstract_chunk_map)

    #print("description:")
    #description
    description_map={}
    #description_chunk_map={}
    desciption = patent_document["description"]
    if desciption != "":
        #print(desciption)
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent-document.description"])
        terms = rt["term_vectors"]["patent-document.description"]["terms"]
        ## terms extraction
        description_map = getTermMap(terms, N, 'description', 1)
        ## phrase extraction
        #chunks = extract_chunks(desciption)
        #description_chunk_map = getChunkMap(chunks, terms, N, 0.3)

        print(description_map)
        #print(description_chunk_map)

    #print("claims:")
    #claims
    claims_map={}
    #claims_chunk_map={}
    claims = patent_document["claims"]
    if claims != "":
        #print(claims)
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent-document.claims"])
        terms = rt["term_vectors"]["patent-document.claims"]["terms"]
        ## terms extraction
        claims_map = getTermMap(terms, N, 'claims', 1)
        ## phrase extraction
        #chunks = extract_chunks(claims)
        #claims_chunk_map = getChunkMap(chunks, terms, N, 0.3)
        print(claims_map)
        #print(claims_chunk_map)


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

    title_str = ' '.join(list(title_map.keys()))
    abstract_str = ' '.join(list(abstract_map.keys()))
    description_str = ' '.join(list(description_map.keys()))
    claims_str = ' '.join(list(claims_map.keys()))
    ipcr_str = ' '.join(list(ipcr_l1))
    print(ipcr_str)

    InitQ = {"title": title_str, "abstract": abstract_str, "description": description_str, "claims": claims_str, "ipcr": ipcr_str}
    #print(InitQ)
    return InitQ


def ReQFormulate(qrel):
    pass


def retrieve(es, qrel):
    #synonym_graph token filter
    #print(' '.join(qrel["title"]))
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

    query1 = {
        "size": 100,
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "patent-document.ipcr": qrel["ipcr"]
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrel["title"],
                            "tie_breaker": 0.5
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
                        "match": {
                            "patent-document.ipcr": qrel["ipcr"]
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrel["abstract"],
                            "analyzer":"stop",
                            "tie_breaker": 0.3
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
                        "match": {
                            "patent-document.ipcr": qrel["ipcr"]
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrel["description"],
                            "tie_breaker": 0.3
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
                        "match": {
                            "patent-document.ipcr": qrel["ipcr"]
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
                ]
            }

        }
    }




    rs = es.search(index="patent", doc_type="patent", body=query2)
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
        'size': 351,
        'query': {
            'match_all': {}
        }
    }
    res = es.search(index='qrel', doc_type='patent', body=doc)

    N = 10469

    for qrel in res["hits"]["hits"]:
        iq = initQFormulate(es,qrel,N)
        rs = retrieve(es,iq)
        result(qrel, rs)


if __name__ == "__main__":
    main()