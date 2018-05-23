##How to Run From Source

###Prerequisites:
1. download patent data CLEF-IP 2010 in http://www.ifs.tuwien.ac.at/~clef-ip/download-central.shtml
1. install elasticsearch.
2. install kibana.
3. run elasticsearch `./elasticsearch`.
4. run kibana `./kibana`.
5. copy the code in 'index.dsl' to the Dev Tools of kibana and run these code to create the qrel index and patent index and initialize the mapping of these two indices.
6. put 'elasticIndex.sh' to the data directory and run this bash code to index the file in the directory `./elasticIndex.sh`.
7. run 'TermVectors.py' to obtain the stop word lists in 'st' folder and document frequency maps in 'df' folder.

###Development Workflow:
1. run 'Retrieval.py' to obtain the retrieval results and write them on file 'result.txt'.
2. run 'Score.py' to calculate the evaluation metrics score.







##The function of each file:
#####Preprocess.py: 
preprocess the patent data. convert XML file to JSON file, merge different versions of a patent into one
patent document, drop the unused sections in the patent document and redesign the structure of the patent document.

####Retrieval.py: 
formulate the query and use the formulated query to search in Elasticsearch. The retrieval results is
outputed in result.txt.

####Score.py: 
calculate the evaluation metrics based on my retrieval output file(result.txt) and the ground true results
file(PAC_qrels_21_EN_mark.txt).

####TermVectors.py: 
generate the field-specific stop word lists and the field-specific term document frequency maps, these
stop word lists and maps are used in the query formulation process.

####VisDataPrepare.py: 
prepare the patent data used in the visualization experiment, such as 'add query key to the related patents',
'mark the result list with lang tag(EN, FR or DE)', 'extract the related patents in the result list and these related patents is used to be stored in the MongoDB used by
the patent retrieval result visualization website'.

