#!/bin/bash

set -e
PACKAGE_NAME=yapsap
cd doc
make clean html
cd ..
pydocstyle ${PACKAGE_NAME}
flake8 ${PACKAGE_NAME}
pylint ${PACKAGE_NAME}
mypy ${PACKAGE_NAME}
pytest --cov-report term-missing
find ${PACKAGE_NAME} -name "*.py" | xargs -I {} pyupgrade --py38-plus {}
pyroma -n 10 .
bandit -r ${PACKAGE_NAME}
scc --no-cocomo --by-file -i py ${PACKAGE_NAME}
