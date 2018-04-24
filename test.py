'''
from googletrans import Translator

translator = Translator()
x = translator.detect('이 문장은 한글로 쓰여졌습니다.')
print(x)

y=translator.detect('この文章は日本語で書かれました。')
print(y)

tr = translator.translate('我是一个程序员', dest='en')
print(tr)

import re
l1 = [1,2,3]
l2=[4,5,6]

for x,y in zip(l1,l2):
    print(x)
    print(y)
    print("-------")


s = 'fsf \n fdfs\n dfs90(a) :fdfs(b)(1);(3).(12),(34)'
print(s)
m = re.findall(r"\(.\)", s)
n = re.findall(r"\(\d\d\)",s)
k = re.findall(r"[,\.:;]",s)
print(m)
print(n)
print(k)
#s=s.replace('(a)',' ')
#print(s)

my_path = '/Users/linhonggu/Desktop/test2/61/71'
if not os.path.exists(my_path):
    os.makedirs(my_path)
'''''


















