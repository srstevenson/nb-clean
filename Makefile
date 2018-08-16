NAME = nb-clean

check:
	pipenv run flake8

format:
	pipenv run yapf -i $(NAME)

upload: check
	pipenv run python setup.py sdist bdist_wheel
	pipenv run twine upload -s dist/*.tar.gz
	pipenv run twine upload -s dist/*.whl

clean:
	$(RM) -r $(wildcard *.egg-info *.pyc) build dist

.PHONY: clean format check upload
