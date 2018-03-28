import json
import xmltodict
import os
import re

def clean(s):
    rt=s.replace('\n', ' ')
    m = re.findall(r"\(.\)", rt)
    n = re.findall(r"\(\d\d\)", rt)
    k = [',','.',':',';']
    for x in m:
        rt=rt.replace(x,'')
    for x in n:
        rt=rt.replace(x,'')
    for x in k:
        rt=rt.replace(x,'')

    return rt

def abst(abstract):
    rt=''
    if isinstance(abstract, list):
        for a in abstract:
            if a['@lang']=='EN':
                if 'p' in a:
                    if isinstance(a['p'], dict):
                        if '#text' in a['p']:
                            rt += a['p']['#text']
                    if isinstance(a['p'], str):
                        rt += a['p']
    elif isinstance(abstract, dict):
        if abstract['@lang'] == 'EN':
            if 'p' in abstract:
                if isinstance(abstract['p'], dict):
                    if '#text' in abstract['p']:
                        rt += abstract['p']['#text']
                elif isinstance(abstract['p'], str):
                    rt += abstract['p']
                elif isinstance(abstract['p'], list):
                    for s in abstract['p']:
                        if isinstance(s,str):
                            rt +=s
                        elif isinstance(s, dict) and '#text' in s:
                            rt += s['#text']
    rt = clean(rt)
    return rt

def tit(title):
    rt=''
    if isinstance(title, list):
        for t in title:
            if t['@lang']=='EN':
                rt=t['#text']
    elif isinstance(title, dict):
        if title['@lang'] == 'EN':
            rt = title['#text']
    elif isinstance(title, str):
        rt = title

    return rt

def des(description):
    rt=''
    if description['@lang']=='EN':
        p = description['p']
        if isinstance(p, list):
            for l in p:
                if isinstance(l,str):
                    rt += l
                elif isinstance(l, dict):
                    if '#text' in l and isinstance(l['#text'], str):
                        rt += l['#text']
        elif isinstance(p, dict):
            pass
        elif isinstance(p, str):
            rt = p

    rt = clean(rt)
    return rt

def ipc(ipcr):
    rt=[]
    if isinstance(ipcr, list):
        for c in ipcr:
            s = c['#text']
            rt.append(s)
    return rt

def cla(claims):
    rt = ''
    if isinstance(claims, dict):
        if claims['@lang']=='EN':
            if 'claim' in claims:
                cla = claims['claim']
                if isinstance(cla, list):
                    for c in cla:
                        if 'claim-text' in c and isinstance(c['claim-text'], str):
                            rt += c['claim-text']
                        elif 'claim-text' in c and isinstance(c['claim-text'], dict):
                            if 'claim-text' in c['claim-text'] and isinstance(c['claim-text']['claim-text'], dict):
                                if 'claim-text' in c['claim-text']['claim-text'] and isinstance(c['claim-text']['claim-text']['claim-text'],list):
                                    for s in c['claim-text']['claim-text']['claim-text']:
                                        if isinstance(s,str):
                                            rt += s
                            elif '#text' in c['claim-text'] and isinstance(c['claim-text']['#text'], str):
                                rt += c['claim-text']['#text']
                elif isinstance(cla, dict):
                    if 'claim-text' in cla and isinstance(cla['claim-text'], str):
                        rt += cla['claim-text']

    elif isinstance(claims, list):
        for co in claims:
            if co['@lang'] == 'EN':
                if 'claim' in co:
                    cla = co['claim']
                    if isinstance(cla, list):
                        for c in cla:
                            if 'claim-text' in c and isinstance(c['claim-text'], str):
                                rt += c['claim-text']
                            elif 'claim-text' in c and isinstance(c['claim-text'], dict):
                                if 'claim-text' in c['claim-text'] and isinstance(c['claim-text']['claim-text'], dict):
                                    if 'claim-text' in c['claim-text']['claim-text'] and isinstance(
                                            c['claim-text']['claim-text']['claim-text'], list):
                                        for s in c['claim-text']['claim-text']['claim-text']:
                                            if isinstance(s,str):
                                                rt += s
                                elif '#text' in c['claim-text'] and isinstance(c['claim-text']['#text'], str):
                                    rt += c['claim-text']['#text']
                    elif isinstance(cla, dict):
                        if 'claim-text' in cla and isinstance(cla['claim-text'], str):
                            rt += cla['claim-text']
                        if 'claim-text' in cla and isinstance(cla['claim-text'], dict):
                            if '#text' in cla['claim-text'] and isinstance(cla['claim-text']['#text'], str):
                                rt += cla['claim-text']['#text']
    rt = clean(rt)
    return rt

def get(path, file):
    with open(os.path.join(path,file), 'r') as f:
        xmlStr = f.read()
    jsonStr = json.dumps(xmltodict.parse(xmlStr), indent=4)
    jsonObj = json.loads(jsonStr)

    lang = jsonObj['patent-document']['@lang']
    if lang == 'EN':
        ucid = jsonObj['patent-document']['@ucid']
        if 'abstract' in jsonObj['patent-document']:
            abstract = abst(jsonObj['patent-document']['abstract'])
        if 'description' in jsonObj['patent-document']:
            description = des(jsonObj['patent-document']['description'])
        if 'claims' in jsonObj['patent-document']:
            claims = cla(jsonObj['patent-document']['claims'])
        if 'technical-data' in jsonObj['patent-document']:
            if 'invention-title' in jsonObj['patent-document']['technical-data']:
                title = tit(jsonObj['patent-document']['bibliographic-data']['technical-data']['invention-title'])
            if 'classifications-ipcr' in jsonObj['patent-document']['technical-data']:
                ipcr = ipc(jsonObj['patent-document']['bibliographic-data']['technical-data']['classifications-ipcr'][
                               'classification-ipcr'])

        my_path = '/Users/linhonggu/Desktop/' + 'test' + path[27:]
        if not os.path.exists(my_path):
            os.makedirs(my_path)

        my_file = file.split('.')[0] + '.json'
        with open(os.path.join(my_path, my_file), 'w') as f:
            f.write(jsonStr)

def unify_s(path, file):
    with open(os.path.join(path,file), 'r') as f:
        xmlStr = f.read();
    jsonStr = json.dumps(xmltodict.parse(xmlStr), indent=4)
    jsonObj = json.loads(jsonStr)

    lang = jsonObj['patent-document']['@lang']
    if lang == 'EN':
        abstract = ''
        description = ''
        claims = ''
        title = ''
        ipcr = []

        ucid = jsonObj['patent-document']['@ucid']
        if 'abstract' in jsonObj['patent-document']:
            abstract = abst(jsonObj['patent-document']['abstract'])
        if 'description' in jsonObj['patent-document']:
            description = des(jsonObj['patent-document']['description'])
        if 'claims' in jsonObj['patent-document']:
            claims = cla(jsonObj['patent-document']['claims'])
        if 'technical-data' in jsonObj['patent-document']['bibliographic-data']:
            if 'invention-title' in jsonObj['patent-document']['bibliographic-data']['technical-data']:
                title = tit(jsonObj['patent-document']['bibliographic-data']['technical-data']['invention-title'])
            if 'classifications-ipcr' in jsonObj['patent-document']['bibliographic-data']['technical-data']:
                ipcr = ipc(jsonObj['patent-document']['bibliographic-data']['technical-data']['classifications-ipcr'][
                               'classification-ipcr'])

        my_jsonDict = {'patent-document': {'ucid': ucid, 'abstract': abstract, 'description': description,
                                           'title': title, 'claims': claims, 'ipcr': ipcr}}

        my_jsonStr = json.dumps(my_jsonDict, indent=4)

        my_path = '/Users/linhonggu/Desktop/' + 'test2' + path[27:]
        if not os.path.exists(my_path):
            os.makedirs(my_path)

        my_file = 'EP-' + file.split('.')[0].split('-')[1] + '.json'
        with open(os.path.join(my_path, my_file), 'w') as f:
            f.write(my_jsonStr)

def unify_m(path, files):
    mis = ['ucid', 'ipcr', 'title', 'abstract', 'description', 'claims']
    ucid = ''
    abstract = ''
    description = ''
    claims = ''
    title = ''
    ipcr = []
    lang=''

    for file in files:
        tmp=[]
        with open(os.path.join(path, file), 'r') as f:
            xmlStr = f.read();
        jsonStr = json.dumps(xmltodict.parse(xmlStr), indent=4)
        jsonObj = json.loads(jsonStr)

        lang = jsonObj['patent-document']['@lang']
        if lang == 'EN':
            for m in mis:
                if m == 'ucid':
                    ucid = jsonObj['patent-document']['@ucid']
                    tmp.append('ucid')
                elif m == 'abstract':
                    if 'abstract' in jsonObj['patent-document']:
                        abstract = abst(jsonObj['patent-document']['abstract'])
                        tmp.append('abstract')
                elif m == 'description':
                    if 'description' in jsonObj['patent-document']:
                        description = des(jsonObj['patent-document']['description'])
                        tmp.append('description')
                elif m == 'claims':
                    if 'claims' in jsonObj['patent-document']:
                        claims = cla(jsonObj['patent-document']['claims'])
                        tmp.append('claims')
                elif m == 'title':
                    if 'technical-data' in jsonObj['patent-document']['bibliographic-data'] and 'invention-title' in jsonObj['patent-document']['bibliographic-data']['technical-data']:
                        title = tit(jsonObj['patent-document']['bibliographic-data']['technical-data']['invention-title'])
                        tmp.append('title')
                elif m == 'ipcr':
                    if 'technical-data' in jsonObj['patent-document']['bibliographic-data'] and 'classifications-ipcr' in jsonObj['patent-document']['bibliographic-data']['technical-data']:
                        ipcr = ipc(
                            jsonObj['patent-document']['bibliographic-data']['technical-data']['classifications-ipcr'][
                                'classification-ipcr'])
                        tmp.append('ipcr')
        for t in tmp:
            mis.remove(t)
        if len(mis) == 0:
            break

    if lang=='EN':
        my_jsonDict = {'patent-document': {'ucid': ucid, 'abstract': abstract, 'description': description,
                                           'title': title, 'claims': claims, 'ipcr': ipcr}}

        my_jsonStr = json.dumps(my_jsonDict, indent=4)

        my_path = '/Users/linhonggu/Desktop/' + 'test2' + path[27:]
        if not os.path.exists(my_path):
            os.makedirs(my_path)

        my_file = 'EP-' + file.split('.')[0].split('-')[1] + '.json'
        with open(os.path.join(my_path, my_file), 'w') as f:
            f.write(my_jsonStr)


def main():
    path = '/Users/linhonggu/Desktop/70'

    for path, subdirs, files in os.walk(path):
        if len(files)!=0 and files[0].split(".")[1]=='xml':
            if len(files) == 1:
                #print(files[0])
                unify_s(path, files[0])
                #get(path, files[0])
            else:
                files.sort(reverse=True)
                unify_m(path, files)
                #for file in files:
                    #get(path, file)


if __name__ == "__main__":
    main()
