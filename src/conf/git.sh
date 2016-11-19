#!/bin/bash
if [ "$#" < 1 ]
then

echo "usage: git up|l|st|ci 'comment'"
exit 1

else
    echo $1
    case $1 in
        "up")
            echo "git pull"
            git pull origin master
        ;;
        "l")
            echo "git log -1 --stat"
            git log -1 --stat
        ;;
        "st")
            echo "git status"
            git status
        ;;
        "ci")
            echo "commit $*"
            shift
            git commit -a -m "$*"
            echo "push"
            git push origin master
        ;;
        *)
            echo "git fetch"
            git fetch origin master
            echo "git merge"
            git merge origin/master
            echo "git status"
            git status
            echo "commit"
            git commit -a -m $1
            echo "push"
            git push origin master
        ;;
    esac 
fi
