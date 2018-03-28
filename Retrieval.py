import math
import enchant
#from nltk import word_tokenize
#from nltk import pos_tag
from elasticsearch import Elasticsearch
#from nltk.corpus import words
import re

'''
#去掉 介词，连词，冠词
def getNoun(str):
    # function to test if something is a noun
    is_noun = lambda pos: pos[:2] == 'NN'
    # do the nlp stuff
    tokenized = word_tokenize(str)
    nouns = [word for (word, pos) in pos_tag(tokenized) if is_noun(pos)]
    print(nouns)
'''

def tfidf(tf,df, N):
    idf = math.log(N/df)
    ti = tf * idf
    return ti

def getTermMap(terms, N, threshold):
    d = enchant.Dict("en_US")
    common = "b,poop,i,ii,iii,v,me,my,myself,we,us,our,ours,ourselves,you,your,yours,yourself,yourselves,he,him,his,himself,she,her,hers,herself,it,its,itself,they,them,their,theirs,themselves,what,which,who,whom,whose,this,that,these,those,am,is,are,was,were,be,been,being,have,has,had,having,do,does,did,doing,will,would,should,can,could,ought,i'm,you're,he's,she's,it's,we're,they're,i've,you've,we've,they've,i'd,you'd,he'd,she'd,we'd,they'd,i'll,you'll,he'll,she'll,we'll,they'll,isn't,aren't,wasn't,weren't,hasn't,haven't,hadn't,doesn't,don't,didn't,won't,wouldn't,shan't,shouldn't,can't,cannot,couldn't,mustn't,let's,that's,who's,what's,here's,there's,when's,where's,why's,how's,a,an,the,and,but,if,or,because,as,until,while,of,at,by,for,with,about,against,between,into,through,during,before,after,above,below,to,from,up,upon,down,in,out,on,off,over,under,again,further,then,once,here,there,when,where,why,how,all,any,both,each,few,more,most,other,some,such,no,nor,not,only,own,same,so,than,too,very,say,says,said,shall,also";
    common_set = set()
    for x in common.split(","):
        common_set.add(x)
    #print(common_set)
    term_map = {}
    for term in terms:
        tmp = re.sub('[!.,?]', '', term)

        if len(tmp) > 1 and (not tmp.isdigit()) and d.check(tmp) and (tmp not in common_set):
            prop = terms[term]
            df = prop["doc_freq"]
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

def assignWeight():
    pass

def initQFormulate(es, qrel, N):
    patent_document = qrel["_source"]["patent_document"]

    #print("title:")
    #title
    title_map={}
    title = patent_document["bibliographic_data"]["technical_data"]["invention_title"]
    if title != "":
        #print(title)
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent_document.bibliographic_data.technical_data.invention_title"], )
        terms = rt["term_vectors"]["patent_document.bibliographic_data.technical_data.invention_title"]["terms"]
        title_map = getTermMap(terms, N, 0.8)
        print(title_map)

    #print("abstract:")
    #abstract
    abstract_map={}
    abstract = patent_document["abstract"]
    if abstract != "":
        #print(abstract)
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent_document.abstract"], )
        terms = rt["term_vectors"]["patent_document.abstract"]["terms"]
        abstract_map = getTermMap(terms, N, 0.7)
        print(abstract_map)

    #print("description:")
    #description
    description_map={}
    desciption = patent_document["description"]["content"]
    if desciption != "":
        #print(desciption)
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent_document.description.content"], )
        terms = rt["term_vectors"]["patent_document.description.content"]["terms"]
        description_map = getTermMap(terms, N, 0.3)
        print(description_map)

    #print("claims:")
    #claims
    claims_map={}
    claims = patent_document["claims"]
    if claims != "":
        #print(claims)
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent_document.claims"], )
        terms = rt["term_vectors"]["patent_document.claims"]["terms"]
        claims_map = getTermMap(terms, N, 0.3)
        print(claims_map)


    #print("IPCR:")
    #IPCR
    ipcr = patent_document["bibliographic_data"]["technical_data"]["classifications_ipcr"]["classification_ipcr"]
    ipcr_l1 = set()
    ipcr_l2 = []
    ipcr_l3 = []
    for ip in ipcr:
        ipcr_l1.add(ip["content"].split()[0])
        ipcr_l2.append(ip["content"].split()[0]+' '+ip["content"].split()[1].split('/')[0])
        ipcr_l3.append(ip["content"].split()[0]+' '+ip["content"].split()[1])

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
                        "fields": ["patent_document.bibliographic_data.technical_data.invention_title^5",
                                   "patent_document.abstract^3", "patent_document.description",
                                   "patent_document.claims"],
                        "query": qrel["title"]
                    }
                    },

                    {"query_string": {
                        "fields": ["patent_document.abstract^3", "patent_document.description",
                                   "patent_document.claims"],
                        "query": qrel["abstract"]
                    }
                    },

                    {"query_string": {
                        "fields": ["patent_document.description"],
                        "query": qrel["description"]
                    }
                    },

                    {"query_string": {
                        "fields": ["patent_document.claims"],
                        "query": qrel["claims"]
                    }
                    },

                    {"query_string": {
                        "fields": ["patent_document.bibliographic_data.technical_data.classifications_ipcr"],
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


    rs = es.search(index="patentcore", doc_type="patent", body=query)
    print(rs["hits"]["total"])
    return rs


def result(qrel, rs):
    hits = rs['hits']['hits']
    i = min(rs["hits"]["total"], 100)
    with open("/Users/linhonggu/Desktop/result.txt",'a') as file:
        for hit in hits:
            if i > 0:
                ucid = hit['_source']['patent_document']['ucid']
                file.write(qrel['_source']['PAC'] + " 0 " + ucid + " 1\n")
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
    res = es.search(index='qrel', doc_type='doc', body=doc)
    N = res["hits"]["total"]

    for qrel in res["hits"]["hits"]:
        #qrel = x["_source"]
        #print(qrel)
        iq = initQFormulate(es,qrel,N)
        rs = retrieve(es,iq)
        result(qrel, rs)


if __name__ == "__main__":
    main()