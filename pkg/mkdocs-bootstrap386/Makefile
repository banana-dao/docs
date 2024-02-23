VERSION = 0.0.1
RELEASE := mkdocs-bootstrap386-$(VERSION)
SRC_DIR := .

.PHONY: clean deploy dist install release uninstall

dist: clean
	python setup.py bdist_wheel sdist --formats gztar

clean:
	rm -rf build dist *.egg-info site tmp

install: dist
	mkdir -p $(SRC_DIR)/tmp
	tar -xf dist/$(RELEASE).tar.gz -C $(SRC_DIR)/tmp
	python $(SRC_DIR)/tmp/$(RELEASE)/setup.py install --record $(SRC_DIR)/tmp/files.txt

uninstall: tmp
	cat $(SRC_DIR)/tmp/files.txt | xargs rm -rf

release:
	twine upload dist/*

deploy:
	mkdocs gh-deploy
