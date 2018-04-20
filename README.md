# NeMo-Eva
The quantitative Network Model Evaluation framework

> Thomas Bläsius, Tobias Friedrich, Maximilian Katzmann, Anton Krohmer and Jonathan Striebel
Towards a Systematic Evaluation of Generative Network Models
[15th Workshop on Algorithms and Models for the Web Graph (2018)](http://www.math.ryerson.ca/waw2018/)
![HPI logo](https://hpi.de/fileadmin/user_upload/hpi/bilder/logos/hpi_logo_web.jpg)

[![CircleCI](https://circleci.com/gh/jstriebel/nemo-eva.svg?style=svg)](https://circleci.com/gh/jstriebel/nemo-eva)

## Usage

You can view the paper results rendered on github within this repo:
* [Graph Features](src/notebooks/graph features.ipynb)
* [Classification Results](src/notebooks/classification results.ipynb)

Adapting the notebooks interactively online migth work in the future with binder (TODO):
[Interactive online notebooks](https://mybinder.org/v2/gh/jstriebel/nemo-eva/master?filepath=src%2Fnotebooks)

To run the experiments and do major changes, please use Docker:

### Docker

Make sure to have recent versions of Docker and docker-compose.

By default, you will use the newest docker images that correspond to the master branch. To change this, explicitly set the image tag, e.g. `DOCKER_TAG=paper`.

Inspect the results from the paper in interactive Jupyter Python notebooks:
```
DATA_PATH=/data-paper/ docker-compose run --rm --service-ports -u $(id -u):$(id -g) nemo-eva
```

Run various commands using mounted volumes:
```
docker-compose run --rm --service-ports -u $(id -u):$(id -g) dev-local
  # Inside the container, you can run the following commands:

  DATA_PATH=/data-paper/ python main.py
  # Reruns the classification with the features used in the paper.
  # This may produce slightly different results, as no seed is used.
  # To run other experiments, please write a similar python script.
  # This script should be improved in the future (issue #2).

  make lint
  make open-notebooks
  make test
  make …
```

To update the docker images, run
```
docker-compose pull
```

Or build them yourself, with
```
docker-compose build
```

Pull Requests are welcome!

## Reproducibility

Many measures have been take to make the experiments reproducible:
* docker images make sure that all dependencies can be met and their versions are consistent
* the analyzed networks are publicly accessible via the [Network Repository](http://networkrepository.com).
* Intermediate results are published in this repo in [paper-data](paper-data).
  * Tests ensure that those results can be reproduced from scratch.
  * The results can be used to run custom classification experiments easily.
* The features we obtained in the paper should therefore be reproducible.
  * An exception are the BA models. For those the python seed was missing in the version we used for the paper. The results are nevertheless very similar, except for the differences coming from randomization.
* The classification is run without seeding and therefore produces slighltly varying results.

## Testing & CI

The different stages of the experiments can be tested in the `dev` container with `make test`.

Building the docker image, running linting and tests is automated in [CircleCI](https://circleci.com/gh/jstriebel/nemo-eva). This is configured [here](.circleci/config.yml).

## Licenses

NeMo-Eva uses data from the [Network Repository](http://networkrepository.com/policy.php). [The extracted data included in this repository](/data-paper) is released under the same terms.

The directly imported python packages are released under the following licenses:

| library | license |
| ------- | ------- |
| aiohttp | Apache 2 |
| backoff | MIT |
| beautifulsoup4 | MIT |
| ipython | BSD |
| jupyter | BSD |
| matplotlib | BSD |
| mpmath | BSD |
| networkit | MIT |
| networkx | BSD |
| numpy | BSD |
| packaging | BSD or Apache License, Version 2.0 |
| pandas | BSD |
| plotly | MIT |
| powerlaw | MIT |
| readline | GNU GPL |
| scikit-learn | new BSD |
| scipy | BSD |
| seaborn | BSD (3-clause) |
| tabulate | MIT |

Additionally, [renderjson.js](src/helpers/renderjson.js) is used, which is released under the ISC License.

All other parts which are created for NeMo-Eva are released under the [MIT License](LICENSE.txt).
