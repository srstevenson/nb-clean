NAME = nb-clean

check:
	mypy --ignore-missing-imports $(NAME)
	flake8 $(NAME)
	pylint -d invalid-name -r n -s n $(NAME)

format:
	yapf -i $(NAME)

upload: check
	python setup.py sdist bdist_wheel upload --sign

clean:
	$(RM) -r $(wildcard *.egg-info *.pyc) build dist

.PHONY: clean format check upload
