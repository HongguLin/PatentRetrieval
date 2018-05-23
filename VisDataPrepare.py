import os
import shutil
import json
from pathlib import Path

# mark the result list with the language it belong to
def markLang():
    enresult = "/Users/linhonggu/Documents/PAC-Qrels/PAC_qrels_21_EN.txt"
    new_enresult = "/Users/linhonggu/Documents/PAC-Qrels/PAC_qrels_21_EN_mark.txt"
    with open(new_enresult, "w") as nf:
        with open(enresult) as f:
            for line in f:
                patent = line.split()[2]
                my_file = Path("/Users/linhonggu/Documents/patent/" + patent + ".json")
                if my_file.is_file():
                    with open("/Users/linhonggu/Documents/patent/" + patent + ".json", "rb") as fin:
                        lang = json.load(fin)["patent_document"]["lang"]
                        nf.write(line.strip("\n")+" "+lang+"\n");

# add Query string to the related patent
def addQkey():
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
                name = 'EP-' + id + '.json'
                if os.path.isfile(os.path.join(path, name)):
                    with open(os.path.join(path, name)) as f:
                        print(name)
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
                        'Qkey': pac,
                        'Qimportance': int(imp)
                    }
                    my_jsonStr = json.dumps(my_jsonDict, indent=4)
                    with open(os.path.join(path1, name), 'w') as f1:
                        # print(my_jsonStr)
                        f1.write(my_jsonStr)

# get the related patent ID set
def getIDSet():
    with open('/Users/linhonggu/Documents/PAC-Qrels/PAC_qrels_21_EN_mark.txt') as f:
        txt = f.read()
    IDset = set()
    for line in txt.split('\n'):
        if isinstance(line, str) and len(line) > 10:
            ucid = line.split()[2]
            lang = line.split()[4]
            if lang == 'EN':
                id = ucid.split('-')[1]
                IDset.add(id)
    return IDset

# the main function
def main():
    markLang()
    addQkey()
    IDSet = getIDSet()
    root = '/Volumes/RG/EP-UNI/000001/'
    for path, subdirs, files in os.walk(root):
        if len(files) != 0 and files[0].split(".")[1] == 'json':
            ucid = files[0].split('.')[0].split('-')[1]
            if ucid in IDSet:
                shutil.copy(os.path.join(path, files[0]), '/Users/linhonggu/Documents/patentcore')

if __name__ == '__main__':
    main()
