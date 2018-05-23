#creat qrel index
PUT /qrel?pretty

#qrel mapping
PUT /qrel
{
  "settings": {
    "analysis": {
      "analyzer": {
        "my_analyzer": {
          "type": "custom",
          "tokenizer": "lowercase",
          "filter": [
            "porter_stem",
            "english_stop"
          ]
        }
      },
      "filter": {
        "english_stop": {
          "type": "stop",
          "stopwords": "_english_"
        }
      }
    }
  },
  "mappings": {
    "patent":{
      "properties": {
        "patent-document":{
          "properties": {
            "PAC":{
              "type":"keyword",
              "store":true
            },
            "ucid":{
              "type":"keyword",
              "store":true
            },
            "abstract":{
              "type":"text",
              "store":true,
              "term_vector": "with_positions_offsets",
              "analyzer":"my_analyzer"
            },
            "description":{
              "type":"text",
              "store":true,
              "term_vector": "with_positions_offsets",
              "analyzer":"my_analyzer"
            },
            "title":{
              "type":"text",
              "store":true,
              "term_vector": "with_positions_offsets",
              "analyzer":"my_analyzer"
            },
            "claims":{
              "type":"text",
              "store":true,
              "term_vector": "with_positions_offsets",
              "analyzer":"my_analyzer"
            }
          }
        }
      }
    }
  }
}

#create patent index
PUT /patent?pretty

#patent mapping
PUT /patent
{
  "settings": {
    "analysis": {
      "analyzer": {
        "my_analyzer": {
          "type": "custom",
          "tokenizer": "lowercase",
          "filter": [
            "porter_stem",
            "english_stop"
          ]
        }
      },
      "filter": {
        "english_stop": {
          "type": "stop",
          "stopwords": "_english_"
        }
      }
    }
  },
  "mappings": {
    "patent":{
      "properties": {
        "patent-document":{
          "properties": {
            "ucid":{
              "type":"keyword"
            },
            "abstract":{
              "type":"text",
              "term_vector": "with_positions_offsets",
              "analyzer":"my_analyzer"
            },
            "description":{
              "type":"text",
              "term_vector": "with_positions_offsets",
              "analyzer":"my_analyzer"
            },
            "title":{
              "type":"text",
              "term_vector": "with_positions_offsets",
              "analyzer":"my_analyzer"
            },
            "claims":{
              "type":"text",
              "term_vector": "with_positions_offsets",
              "analyzer":"my_analyzer"
            }
          }
        }
      }
    }
  }
}