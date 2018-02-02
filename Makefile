all: install

install:
	python setup.py install

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/
	rm -rf *.egg-info
	rm -rf *.egg
	rm -rf *.pyc
	rm -rf *.pyo
	rm -rf *~
	rm -rf __pycache__