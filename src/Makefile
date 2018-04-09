DATA_FOLDERS = $(subst /,,$(subst ../data/,,$(dir $(wildcard ../data/*/results.csv))))

open-notebooks:
	HOME=/src PYTHONPATH=$$(pwd) \
	jupyter-notebook -y --ip=0.0.0.0 --no-browser notebooks

render-notebooks:
	export HOME=/src && \
	export PYTHONPATH=$$(pwd) && \
	cd notebooks && \
	for f in "*.ipynb"; do \
		jupyter nbconvert \
			--ExecutePreprocessor.timeout=6000\
			--execute \
			--to notebook \
			--inplace \
			"$$f"; \
	done && \
	jupyter trust *.ipynb

lint:
	pycodestyle --show-source --show-pep8 --max-line-length 120 .

test:
	Xvfb $$DISPLAY -screen 0 800x600x8 -ac +render -noreset &
	pytest -s tests/*.py

clean: $(addprefix clean-, $(DATA_FOLDERS))

$(addprefix clean-, $(DATA_FOLDERS)):clean-%: ../data/%
	rm -rf "$^"

.PHONY: open-notebooks
