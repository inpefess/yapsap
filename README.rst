..
  Copyright 2021-2023 Boris Shminke

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

|PyPI version|\ |CircleCI|\ |Documentation Status|\ |codecov|

yapsap
======

``yapsap`` is Yet Another Python SAturation-style Prover. Currently,
it can only prove theorems in `TPTP library <https://tptp.org>`__
formal language in `clausal normal form
<https://en.wikipedia.org/wiki/Conjunctive_normal_form>`__.
``yapsap`` implements the `given clause algorithm
<https://royalsocietypublishing.org/doi/10.1098/rsta.2018.0034#d3e468>`__
and was inspired by `PyRes <https://github.com/eprover/PyRes>`__.

How to Install
==============

The best way to install this package is to use ``pip``:

.. code:: sh

   pip install git+https://github.com/inpefess/yapsap.git

How to use
==========

.. code:: python

   from random import choice, seed

   from yapsap import YapsaProver


   class RandomProver(YapsaProver):
       def proof_attempt(self) -> None:
           while not self.proof_found:
               self._step(choice(list(self.state.keys())))


   prover = RandomProver(
       "./yapsap/resources/TPTP-mock/Problems/TST/TST001-1.p"
   )
   seed(0)
   prover.proof_attempt()
   print(prover.state)

How to Contribute
=================

`Pull requests <https://github.com/inpefess/yapsap/pulls>`__ are
welcome. To start:

.. code:: sh

   git clone https://github.com/inpefess/yapsap
   cd yapsap
   # activate python virtual environment with Python 3.8+
   pip install -U pip
   pip install -U setuptools wheel poetry
   poetry install
   # recommended but not necessary
   pre-commit install
   
To check the code quality before creating a pull request, one might
run the script ``local-build.sh``. It locally does nearly the same as
the CI pipeline after the PR is created.

Reporting issues or problems with the software
==============================================

Questions and bug reports are welcome on `the
tracker <https://github.com/inpefess/yapsap/issues>`__.

More documentation
==================

More documentation can be found
`here <https://yapsap.readthedocs.io/en/latest>`__.

.. |PyPI version| image:: https://badge.fury.io/py/yapsap.svg
   :target: https://badge.fury.io/py/yapsap
.. |CircleCI| image:: https://circleci.com/gh/inpefess/yapsap.svg?style=svg
   :target: https://circleci.com/gh/inpefess/yapsap
.. |Documentation Status| image:: https://readthedocs.org/projects/yapsap/badge/?version=latest
   :target: https://yapsap.readthedocs.io/en/latest/?badge=latest
.. |codecov| image:: https://codecov.io/gh/inpefess/yapsap/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/inpefess/yapsap
