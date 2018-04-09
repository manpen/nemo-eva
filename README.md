# NeMo-Eva
The quantitative Network Model Evaluation framework

[CI overview](https://circleci.com/gh/jstriebel/nemo-eva)

```
docker-compose build nemo-eva && docker-compose run --rm nemo-eva
```

Pull Requests are welcome!

## Future Work

NOTE: correlation based on real-world + all models

## Licenses

NeMo-Eva uses data from the [Network Repository](http://networkrepository.com/policy.php). [The extracted data included in this repository](/data) is released under the same terms.

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
