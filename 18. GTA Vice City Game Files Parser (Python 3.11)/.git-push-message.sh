#!/bin/bash
git add -A
read -p "Message: " msg
git commit -m "$msg"
git push
read -p "Press any key to exit..."