NAME = nb-clean

upload:
	pipenv run python setup.py sdist bdist_wheel
	pipenv run twine upload -s dist/*.tar.gz
	pipenv run twine upload -s dist/*.whl

clean:
	$(RM) -r $(wildcard *.egg-info *.pyc) build dist

.PHONY: clean upload
