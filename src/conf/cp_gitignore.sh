#!/bin/bash

ls -A > dir.log

while read line ; 
do 
    if [ -d $line ]; 
    then 
        echo "$line"; 
        cp .gitignore $line
    else 
        false; 
    fi; 
done < dir.log