#!/bin/bash
FILES=$(find . -name "*.json")
for f in ${FILES}
do
echo "Processing file...";
curl -H "Content-Type: application/json" -XPOST "localhost:9200/patent/patent?pretty&refresh" --data-binary "@$f";
done