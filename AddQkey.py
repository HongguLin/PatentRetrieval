import os
import json
path = '/Users/linhonggu/Documents/patentcore/'
path1 = '/Users/linhonggu/Documents/patentcore1/'
with open('/Users/linhonggu/Documents/PAC-Qrels/PAC_qrels_21_EN_mark.txt') as f:
    txt = f.read()
for line in txt.split('\n'):
    if isinstance(line, str) and len(line) > 10:
        pac = line.split()[0]
        imp = line.split()[3]
        ucid = line.split()[2]
        lang = line.split()[4]
        if lang == 'EN':
            id = ucid.split('-')[1]
            name = 'EP-'+id+'.json'
            if os.path.isfile(os.path.join(path,name)):
                with open(os.path.join(path, name)) as f:
                    print(name)
                    jsonStr = f.read()
                jsonObj = json.loads(jsonStr)
                patent_document = jsonObj['patent-document']
                my_jsonDict = {
                    'patent_document':{
                        'ucid': patent_document['ucid'],
                        'abstract': patent_document['abstract'],
                        'description': patent_document['description'],
                        'title': patent_document['title'],
                        'claims': patent_document['claims'],
                        'ipcr': patent_document['ipcr']
                    },
                    'Qkey': pac,
                    'Qimportance': int(imp)
                }
                my_jsonStr = json.dumps(my_jsonDict, indent=4)
                with open(os.path.join(path1, name), 'w') as f1:
                    #print(my_jsonStr)
                    f1.write(my_jsonStr)



