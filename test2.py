import os
path = '/Users/linhonggu/Documents/Topics-2010/'
for filename in os.listdir(path):
    with open(os.path.join(path,filename)) as f:
        xmlStr = f.read()
