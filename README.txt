Preprocess.py: preprocess the patent data. convert XML file to JSON file, merge different versions of a patent into one
patent document, drop the unused sections in the patent document and redesign the structure of the patent document.

Retrieval.py: formulate the query and use the formulated query to search in Elasticsearch. The retrieval results is
outputed in result.txt.

Score.py: calculate the evaluation metrics based on my retrieval output file(result.txt) and the ground true results
file(PAC_qrels_21_EN_mark.txt).

TermVectors.py: generate the field-specific stop word lists and the field-specific term document frequency maps, these
stop word lists and maps are used in the query formulation process.

AddQkey.py: add query key to the related patents.

ExtractCorePatent.py: extract the related patents in the result list and these related patents is used to be stored in
the MongoDB used by the patent retrieval result visualization website.

Mark.py: mark the result list with lang tag(EN, FR or DE).