import math
import enchant
from elasticsearch import Elasticsearch
import re
import itertools, nltk, string, gensim
from nltk.stem import WordNetLemmatizer
import json
from itertools import takewhile, tee
import networkx
from nltk.corpus import wordnet as wn

def lambda_unpack(f):
    return lambda args: f(*args)

def tfidf(tf,df, N):
    idf = math.log(N/df)
    ti = tf * idf
    return ti

def getTermMap(terms, N, threshold):
    d = enchant.Dict("en_US")
    with open('englishST.txt') as f:
        stop = f.read()
    #common = "b,poop,i,ii,iii,v,me,my,myself,we,us,our,ours,ourselves,you,your,yours,yourself,yourselves,he,him,his,himself,she,her,hers,herself,it,its,itself,they,them,their,theirs,themselves,what,which,who,whom,whose,this,that,these,those,am,is,are,was,were,be,been,being,have,has,had,having,do,does,did,doing,will,would,should,can,could,ought,i'm,you're,he's,she's,it's,we're,they're,i've,you've,we've,they've,i'd,you'd,he'd,she'd,we'd,they'd,i'll,you'll,he'll,she'll,we'll,they'll,isn't,aren't,wasn't,weren't,hasn't,haven't,hadn't,doesn't,don't,didn't,won't,wouldn't,shan't,shouldn't,can't,cannot,couldn't,mustn't,let's,that's,who's,what's,here's,there's,when's,where's,why's,how's,a,an,the,and,but,if,or,because,as,until,while,of,at,by,for,with,about,against,between,into,through,during,before,after,above,below,to,from,up,upon,down,in,out,on,off,over,under,again,further,then,once,here,there,when,where,why,how,all,any,both,each,few,more,most,other,some,such,no,nor,not,only,own,same,so,than,too,very,say,says,said,shall,also,a’s, able, about, above, according, accordingly, across, actually, after, afterwards, again, against, ain’t, all, allow, allows, almost, alone, along, already, also, although, always, am, among, amongst, an, and, another, any, anybody, anyhow, anyone, anything, anyway, anyways, anywhere, apart, appear, appreciate, appropriate, are, aren’t, around, as, aside, ask, asking, associated, at, available, away, awfully, be, became, because, become, becomes, becoming, been, before, beforehand, behind, being, believe, below, beside, besides, best, better, between, beyond, both, brief, but, by, c’mon, c’s, came, can, can’t, cannot, cant, cause, causes, certain, certainly, changes, clearly, co, com, come, comes, concerning, consequently, consider, considering, contain, containing, contains, corresponding, could, couldn’t, course, currently, definitely, described, despite, did, didn’t, different, do, does, doesn’t, doing, don’t, done, down, downwards, during, each, edu, eg, eight, either, else, elsewhere, enough, entirely, especially, et, etc, even, ever, every, everybody, everyone, everything, everywhere, ex, exactly, example, except, far, few, fifth, first, five, followed, following, follows, for, former, formerly, forth, four, from, further, furthermore, get, gets, getting, given, gives, go, goes, going, gone, got, gotten, greetings, had, hadn’t, happens, hardly, has, hasn’t, have, haven’t, having, he, he’s, hello, help, hence, her, here, here’s, hereafter, hereby, herein, hereupon, hers, herself, hi, him, himself, his, hither, hopefully, how, howbeit, however, i’d, i’ll, i’m, i’ve, ie, if, ignored, immediate, in, inasmuch, inc, indeed, indicate, indicated, indicates, inner, insofar, instead, into, inward, is, isn’t, it, it’d, it’ll, it’s, its, itself, just, keep, keeps, kept, know, knows, known, last, lately, later, latter, latterly, least, less, lest, let, let’s, like, liked, likely, little, look, looking, looks, ltd, mainly, many, may, maybe, me, mean, meanwhile, merely, might, more, moreover, most, mostly, much, must, my, myself, name, namely, nd, near, nearly, necessary, need, needs, neither, never, nevertheless, new, next, nine, no, nobody, non, none, noone, nor, normally, not, nothing, novel, now, nowhere, obviously, of, off, often, oh, ok, okay, old, on, once, one, ones, only, onto, or, other, others, otherwise, ought, our, ours, ourselves, out, outside, over, overall, own, particular, particularly, per, perhaps, placed, please, plus, possible, presumably, probably, provides, que, quite, qv, rather, rd, re, really, reasonably, regarding, regardless, regards, relatively, respectively, right, said, same, saw, say, saying, says, second, secondly, see, seeing, seem, seemed, seeming, seems, seen, self, selves, sensible, sent, serious, seriously, seven, several, shall, she, should, shouldn’t, since, six, so, some, somebody, somehow, someone, something, sometime, sometimes, somewhat, somewhere, soon, sorry, specified, specify, specifying, still, sub, such, sup, sure, t’s, take, taken, tell, tends, th, than, thank, thanks, thanx, that, that’s, thats, the, their, theirs, them, themselves, then, thence, there, there’s, thereafter, thereby, therefore, therein, theres, thereupon, these, they, they’d, they’ll, they’re, they’ve, think, third, this, thorough, thoroughly, those, though, three, through, throughout, thru, thus, to, together, too, took, toward, towards, tried, tries, truly, try, trying, twice, two, un, under, unfortunately, unless, unlikely, until, unto, up, upon, us, use, used, useful, uses, using, usually, value, various, very, via, viz, vs, want, wants, was, wasn’t, way, we, we’d, we’ll, we’re, we’ve, welcome, well, went, were, weren’t, what, what’s, whatever, when, whence, whenever, where, where’s, whereafter, whereas, whereby, wherein, whereupon, wherever, whether, which, while, whither, who, who’s, whoever, whole, whom, whose, why, will, willing, wish, with, within, without, won’t, wonder, would, would, wouldn’t, yes, yet, you, you’d, you’ll, you’re, you’ve, your, yours, yourself, yourselves, zero";
    stop_set = set()
    for x in stop.split(","):
        stop_set.add(x.strip())
    #print(common_set)
    term_map = {}
    for term in terms:
        tmp = re.sub('[!.,?]', '', term)

        if len(tmp) > 1 and (not tmp.isdigit()) and d.check(tmp) and (tmp not in stop_set):
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
    patent_document = qrel["_source"]["patent_document"]

    #print("title:")
    #title
    title_map={}
    #title_chunk_map={}
    title = patent_document["bibliographic_data"]["technical_data"]["invention_title"]
    if title != "":
        #print(title)
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent_document.bibliographic_data.technical_data.invention_title"], )
        terms = rt["term_vectors"]["patent_document.bibliographic_data.technical_data.invention_title"]["terms"]
        ## terms extraction
        title_map = getTermMap(terms, N, 0.8)
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
                            fields=["patent_document.abstract"], )
        terms = rt["term_vectors"]["patent_document.abstract"]["terms"]
        ## terms extraction
        abstract_map = getTermMap(terms, N, 0.8)
        ## phrase extraction
        #chunks = extract_chunks(abstract)
        #abstract_chunk_map = getChunkMap(chunks, terms, N, 0.7)

        print(abstract_map)
        #print(abstract_chunk_map)

    #print("description:")
    #description
    description_map={}
    #description_chunk_map={}
    desciption = patent_document["description"]["content"]
    if desciption != "":
        #print(desciption)
        rt = es.termvectors(index=qrel["_index"], doc_type=qrel["_type"], id=qrel["_id"], field_statistics=True,
                            term_statistics=True,
                            fields=["patent_document.description.content"], )
        terms = rt["term_vectors"]["patent_document.description.content"]["terms"]
        ## terms extraction
        description_map = getTermMap(terms, N, 0.3)
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
                            fields=["patent_document.claims"], )
        terms = rt["term_vectors"]["patent_document.claims"]["terms"]
        ## terms extraction
        claims_map = getTermMap(terms, N, 0.3)
        ## phrase extraction
        #chunks = extract_chunks(claims)
        #claims_chunk_map = getChunkMap(chunks, terms, N, 0.3)
        print(claims_map)
        #print(claims_chunk_map)


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
                            "tie_breaker": 0.3
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
                            "tie_breaker": 0.2
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
        iq = initQFormulate(es,qrel,N)
        rs = retrieve(es,iq)
        result(qrel, rs)


if __name__ == "__main__":
    main()