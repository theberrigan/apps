#!/bin/bash
cd ..
git add -A
git commit -m "$( date +"%d.%m.%Y %H:%M:%S" )"
git push
read -p "Press any key to exit..."