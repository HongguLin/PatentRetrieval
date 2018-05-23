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

# load document frequency map
def load_obj(name):
    with open('df/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def lambda_unpack(f):
    return lambda args: f(*args)

# calculate and return TF*IDF score
def tfidf(tf,df, N):
    idf = math.log(N/df)
    ti = tf * idf
    return ti


# baseline query formulation
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

# term selection query formulation
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

## key phrase selection query formulation
 # extract noun phrase candidates
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
 #
 # select key phrase within the noun phrase candidates
def phraseSelection(chunks, terms, N, sec, threshold):
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
        if len(l)>3 or len(l)==1:
            continue
        for ll in l:
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
    if(size>0):
        for k, v in tmp:
            k = re.sub('[!.,?]', ' ', k)
            if i < size:
                rt[k] = v
                phrase_str += "\"" + k + "\"" + " OR "
            i = i + 1
        phrase_str = phrase_str[0:-3]
    else:
        phrase_str = ""


    return phrase_str


# extract common term within four different sections
def extract_common_term(tit, abst, des, cla):
    title = set(tit.split())
    abstract = set(abst.split())
    description = set(des.split())
    claims = set(cla.split())

    x4 = title & abstract & description & claims
    com4 = ' '.join(list(x4))

    x3_1 = title & abstract & description
    x3_2 = title & abstract & claims
    x3_3 = title & description & claims
    x3_4 = abstract & description & claims
    x3 = x3_1 | x3_2 | x3_3 | x3_4
    com3 = ' '.join(list(x3))

    x2_1 = title & abstract
    x2_2 = title & description
    x2_3 = title & claims
    x2_4 = abstract & description
    x2_5 = abstract & claims
    x2_6 = description & claims
    x2 = x2_1 | x2_2 | x2_3 | x2_4 | x2_5 | x2_6
    com2 = ' '.join(list(x2))

    return {'com2':com2, 'com3':com3, 'com4':com4}

# extract common phrase within four different sections
def extract_common_phrase(tit, abst, des, cla):
    if tit == '':
        title = set([])
    else:
        title = set(tit.split(' OR '))

    if abst == '':
        abstract = set([])
    else:
        abstract = set(abst.split(' OR '))

    if des == '':
        description = set([])
    else:
        description = set(des.split(' OR '))

    if cla == '':
        claims = set([])
    else:
        claims = set(cla.split(' OR '))

    x4 = title & abstract & description & claims
    com4 = ' OR '.join(list(x4))

    x3_1 = title & abstract & description
    x3_2 = title & abstract & claims
    x3_3 = title & description & claims
    x3_4 = abstract & description & claims
    x3 = x3_1 | x3_2 | x3_3 | x3_4
    com3 = ' OR '.join(list(x3))

    x2_1 = title & abstract
    x2_2 = title & description
    x2_3 = title & claims
    x2_4 = abstract & description
    x2_5 = abstract & claims
    x2_6 = description & claims
    x2 = x2_1 | x2_2 | x2_3 | x2_4 | x2_5 | x2_6
    com2 = ' OR '.join(list(x2))

    return {'com2':com2, 'com3':com3, 'com4':com4}


# initial query formulate
def initQFormulate(es, qrel, N):
    patent_document = qrel["_source"]["patent-document"]

    #title
    title_str = ''
    title_phrase = ''
    title = patent_document["title"]
    if title != "":
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent-document.title"])
        terms = rt["term_vectors"]["patent-document.title"]["terms"]

        ## baseline
        title_str = baseline(terms, 'title')

        ## terms extraction
        #title_str = termSelection(terms, N, 'title', 1)

        ## phrase extraction
        chunks = extract_chunks(title)
        title_phrase = phraseSelection(chunks,terms,N,'title',1)

        #print(title_str)
        #print(title_phrase)

    #abstract
    abstract_str=''
    abstract_phrase = ''
    abstract = patent_document["abstract"]
    if abstract != "":
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent-document.abstract"])
        terms = rt["term_vectors"]["patent-document.abstract"]["terms"]

        ## baseline
        abstract_str = baseline(terms, 'abstract')

        ## terms extraction
        #abstract_str = termSelection(terms, N, 'abstract', 1)

        ## phrase extraction
        chunks = extract_chunks(abstract)
        abstract_phrase = phraseSelection(chunks, terms, N, 'abstract', 1)

        #print(abstract_str)
        #print(abstract_phrase)

    #description
    description_str=''
    description_phrase = ''
    desciption = patent_document["description"]
    if desciption != "":
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent-document.description"])
        terms = rt["term_vectors"]["patent-document.description"]["terms"]
        ## baseline
        description_str = baseline(terms, 'description')
        ## terms extraction
        #description_str = termSelection(terms, N, 'description', 1)

        ## phrase extraction
        chunks = extract_chunks(desciption)
        description_phrase = phraseSelection(chunks, terms, N, 'description', 0.9)

        #print(description_str)
        #print(description_phrase)

    #claims
    claims_str=''
    claims_phrase = ''
    claims = patent_document["claims"]
    if claims != "":
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent-document.claims"])
        terms = rt["term_vectors"]["patent-document.claims"]["terms"]
        ## baseline
        claims_str = baseline(terms, 'claims')

        ## terms extraction
        #claims_str = termSelection(terms, N, 'claims', 1)

        ## phrase extraction
        chunks = extract_chunks(claims)
        claims_phrase = phraseSelection(chunks, terms, N, 'claims', 0.8)

        #print(claims_str)
        #print(claims_phrase)


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
    #print(ipcr_str)


    InitQ = {"title": title_str, "abstract": abstract_str, "description": description_str, "claims": claims_str, "ipcr": ipcr_str}
    InitQP = {"title": title_phrase, "abstract": abstract_phrase, "description": description_phrase, "claims": claims_phrase, "ipcr": ipcr_str}
    InitQCom = extract_common_term(title_str, abstract_str, description_str, claims_str)
    InitQPCom = extract_common_phrase(title_phrase, abstract_phrase, description_phrase, claims_phrase)

    return InitQ, InitQP, InitQCom, InitQPCom

# query reformulate[future work]
def ReQFormulate(qrel):
    pass

# retrieve query
def retrieve(es, qrel, qrelP, qrelCom, qrelPCom):

    # title section query
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

    # abstract section query
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

    # description section query
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

    # claims section query
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

    # combination1 query
    query_comb1 = {
        "size": 100,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "fields": ["patent-document.title"],
                            "query": qrel["title"],
                            "tie_breaker": 0.3
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.abstract"],
                            "query": qrel["abstract"],
                            "tie_breaker": 0.3
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.description"],
                            "query": qrel["description"],
                            "tie_breaker": 0.3
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.claims"],
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

    # combination2 query
    query_comb2 = {
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

    # combination2 + common term query
    query_comm_term = {
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
                "should":[
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrelCom["com2"],
                            "tie_breaker": 0.3
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrelCom["com3"],
                            "tie_breaker": 0.3
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrelCom["com4"],
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

    # combination2 + phrase search query
    query_phrase = {
        "size": 100,
        "query": {
            "bool": {
                "should": [
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
                    }
                ],
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

    # combination2 + phrase search + common term query
    query_phrase_comm_term = {
        "size": 100,
        "query": {
            "bool": {
                "should": [
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

                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrelCom["com2"],
                            "tie_breaker": 0.3
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrelCom["com3"],
                            "tie_breaker": 0.3
                        }
                    },
                    {
                        "multi_match": {
                            "fields": ["patent-document.title", "patent-document.abstract",
                                       "patent-document.description", "patent-document.claims"],
                            "query": qrelCom["com4"],
                            "tie_breaker": 0.3
                        }
                    }
                ],
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

    rs = es.search(index="patent", doc_type="patent", body=query_phrase_comm_term, timeout='60s', request_timeout=60)
    print(rs["hits"]["total"])
    return rs

# write the retrieval result to 'result.txt'
def result(qrel, rs):
    hits = rs['hits']['hits']
    i = min(rs["hits"]["total"], 100)
    with open("result.txt",'a') as file:
        for hit in hits:
            if i > 0:
                ucid = hit['_source']['patent-document']['ucid']
                file.write(qrel['_source']['patent-document']['PAC'] + " 0 " + ucid + " 1\n")
            i = i - 1


# main function
def main():
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
        iq, iqp, iqcom, iqpcom = initQFormulate(es,qrel,N)
        rs = retrieve(es, iq, iqp, iqcom, iqpcom)
        result(qrel, rs)


if __name__ == "__main__":
    main()