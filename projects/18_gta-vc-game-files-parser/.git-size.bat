@echo off
git gc --aggressive --prune
git count-objects -vH
pause