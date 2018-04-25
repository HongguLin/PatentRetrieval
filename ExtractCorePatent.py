import os
import shutil
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

IDSet = getIDSet()

root = '/Volumes/RG/EP-UNI/000001/'
for path, subdirs, files in os.walk(root):
    if len(files)!=0 and files[0].split(".")[1]=='json':
        ucid = files[0].split('.')[0].split('-')[1]
        if ucid in IDSet:
            shutil.copy(os.path.join(path,files[0]), '/Users/linhonggu/Documents/patentcore')