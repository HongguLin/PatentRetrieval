from elasticsearch import Elasticsearch
import math
import pickle
def getTermVectors(es,resL,sec):
    vectorsMap = {}
    for res in resL:
        for patent in res["hits"]["hits"]:
            vecs = es.termvectors(index=patent["_index"], doc_type=patent["_type"], id=patent["_id"],
                                  field_statistics=True,
                                  term_statistics=True, fields=["patent-document." + sec])
            if "patent-document." + sec in vecs["term_vectors"]:
                terms = vecs["term_vectors"]["patent-document." + sec]["terms"]
                for key, value in terms.items():
                    if key not in vectorsMap.keys():
                        vectorsMap[key] = value['doc_freq']

    sortedTupes = sorted(vectorsMap.items(),key=lambda x:x[1], reverse=True)
    l = len(sortedTupes)*0.05
    print(l)
    i=0
    with open(sec+'ST.txt','w') as f:
        for tu in sortedTupes:
            if i<l:
                f.write(tu[0]+'\n')
            i = i+1

    return vectorsMap

def save_obj(obj, name ):
    with open('df/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('df/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def main():
    es = Elasticsearch(['http://localhost:9200/'])
    matchAll = {
        'query': {
            'match_all': {}
        }
    }
    N = es.count(index='patentcore', doc_type='patent', body=matchAll)['count']
    print(N)
    batches = math.floor(N/10000)
    query = {
        'size': 10000,
        'query': {
            'match_all': {}
        }
    }
    resL=[]
    res0 = es.search(index='patentcore', doc_type='patent', body=query, scroll='1m')
    print(len(res0['hits']['hits']))
    resL.append(res0)
    scroll = res0['_scroll_id']
    for i in range(batches):
        res = es.scroll(scroll_id=scroll, scroll='1m')
        print(len(res['hits']['hits']))
        scroll = res['_scroll_id']
        resL.append(res)

    titVec = getTermVectors(es, resL, 'title')
    save_obj(titVec, 'titDF')
    absVec = getTermVectors(es, resL, 'abstract')
    save_obj(absVec, 'absDF')
    desVec = getTermVectors(es, resL, 'description')
    save_obj(desVec, 'desDF')
    claVec = getTermVectors(es, resL, 'claims')
    save_obj(claVec, 'claDF')


if __name__ == "__main__":
    main()