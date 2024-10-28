# See the INSTALL.md notes on how to use this Makefile

#
SHELL = /bin/bash

#
TIME = /usr/bin/time

URL1 = https://github.com/CasaGuides/CASA-Guides-Script-Extractor


.PHONY:  help install build


## help:      This Help
help : Makefile
	@sed -n 's/^##//p' $<


install:
	@echo "none yet"


## git:       Get all git repos for this install
git:  $(GIT_DIRS)
	@echo Last git: `date` >> git.log

## pull:      Update all git repos
pull:
	@echo -n "lmtoy: "; git pull
	-@for dir in $(GIT_DIRS); do\
	(echo -n "$$dir: " ;cd $$dir; git pull); done
	@echo Last pull: `date` >> git.log

status:
	@echo -n "lmtoy: "; git status -uno
	-@for dir in $(GIT_DIRS); do\
	(echo -n "$$dir: " ;cd $$dir; git status -uno); done

branch:
	@echo -n "lmtoy: "; git branch --show-current
	-@for dir in $(GIT_DIRS); do\
	(echo -n "$$dir: " ;cd $$dir; git branch --show-current); done

CASA-Guides-Script-Extractor:
	git clone $(URL1)

