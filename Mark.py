import json
from pathlib import Path

def markLang(enresult, new_enresult):
    with open(new_enresult, "w") as nf:
        with open(enresult) as f:
            for line in f:
                patent = line.split()[2]
                my_file = Path("/Users/linhonggu/Documents/patent/" + patent + ".json")
                if my_file.is_file():
                    with open("/Users/linhonggu/Documents/patent/" + patent + ".json", "rb") as fin:
                        lang = json.load(fin)["patent_document"]["lang"]
                        nf.write(line.strip("\n")+" "+lang+"\n");


enresult = "/Users/linhonggu/Documents/PAC-Qrels/PAC_qrels_21_EN.txt"
new_enresult = "/Users/linhonggu/Documents/PAC-Qrels/PAC_qrels_21_EN_mark.txt"
markLang(enresult, new_enresult)