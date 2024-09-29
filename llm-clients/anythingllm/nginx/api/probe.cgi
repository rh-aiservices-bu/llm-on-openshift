#!/bin/bash
if [[ $(ps -aux | grep node | grep /app/server/index.js) ]]; then
    echo "Status: 200"
    echo "Content-type: text/html"
    echo
    echo  "<html><body>AnythingLLM is running!</body></html>"
else
    echo "Status: 404"
    echo "Content-type: text/html"
    echo ""
    echo "<html><body>AnythingLLM is not running!</body></html>"
fi