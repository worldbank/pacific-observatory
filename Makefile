
all:
	jupyter-book clean docs
	jupyter-book build docs
	open docs/_build/html/index.html
