import os
import json
path = '/Users/linhonggu/Documents/Topics-2010-JSON/'
path1 = '/Users/linhonggu/Documents/Topics-2010-JSON1/'
for filename in os.listdir(path):
    if filename.split(".")[1]=='json':
        with open(os.path.join(path,filename)) as f:
            jsonStr = f.read()
        jsonObj = json.loads(jsonStr)
        patent_document = jsonObj['patent-document']
        my_jsonDict = {
            'patent_document': {
                'ucid': patent_document['ucid'],
                'abstract': patent_document['abstract'],
                'description': patent_document['description'],
                'title': patent_document['title'],
                'claims': patent_document['claims'],
                'ipcr': patent_document['ipcr']
            },
            'PAC': patent_document['PAC'],
        }
        my_jsonStr = json.dumps(my_jsonDict, indent=4)
        with open(os.path.join(path1, filename), 'w') as f1:
            # print(my_jsonStr)
            f1.write(my_jsonStr)


















