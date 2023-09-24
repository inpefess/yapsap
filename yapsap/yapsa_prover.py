# Copyright 2021-2023 Boris Shminke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# noqa: D205, D400
"""
Saturation Prover
=================
"""
import dataclasses
import os
from typing import Dict, Set, Tuple

import orjson
from tptp_lark_parser.grammar import Clause
from tptp_lark_parser.tptp_parser import TPTPParser

from yapsap.factoring import all_possible_factors
from yapsap.paramodulation import all_paramodulants_from_list
from yapsap.reflexivity_resolution import all_possible_reflexivity_resolvents
from yapsap.resolution import all_possible_resolvents
from yapsap.utils import is_tautology, reindex_variables


class YapsaProver:
    """
    Saturation algorithm defined in a Reinforcement Learning friendly way.

    >>> import sys
    >>> if sys.version_info.major == 3 and sys.version_info.minor >= 9:
    ...     from importlib.resources import files
    ... else:
    ...     from importlib_resources import files
    >>> tptp_folder = files("yapsap").joinpath(
    ...     os.path.join("resources", "TPTP-mock")
    ... )
    >>> problem = os.path.join(tptp_folder, "Problems", "TST", "TST001-1.p")
    >>> from random import choice
    >>> class RandomProver(YapsaProver):
    ...     def proof_attempt(self) -> None:
    ...         while not self.proof_found:
    ...             self._step(choice(list(self.state.keys())))
    ...
    >>> prover = RandomProver(problem)
    >>> len(prover.state)
    4

    >>> from random import seed
    >>> seed(0)
    >>> prover.proof_attempt()
    >>> print(len(prover.state))
    161
    """

    def __init__(self, problem: str):
        """
        Initialise spaces et al.

        :param problem: a list of the names of TPTP problem files
        """
        self.state: Dict[str, Clause] = {}
        self._state_set: Set[Tuple[bytes, ...]] = set()
        self.problem = problem
        tptp_folder = os.path.join(os.path.dirname(problem), "..", "..")
        self._tptp_parser = TPTPParser(tptp_folder, extendable=True)
        self.state = reindex_variables(self._init_clauses())
        self._state_set = set(
            map(
                lambda clause: tuple(
                    sorted(map(orjson.dumps, clause.literals))
                ),
                self.state.values(),
            )
        )

    def _init_clauses(self) -> Dict[str, Clause]:
        with open(self.problem, encoding="utf-8") as problem_file:
            problem_text = problem_file.read()
        parsed_clauses = self._tptp_parser.parse(problem_text)
        return {
            clause.label: dataclasses.replace(
                clause,
                birth_step=0,
                inference_parents=(),
                inference_rule=None,
                processed=False,
            )
            for clause in parsed_clauses
        }

    def _add_to_state(self, new_clauses: Tuple[Clause, ...]) -> None:
        birth_step = 1 + self._last_birth_step
        for clause in new_clauses:
            if not is_tautology(clause):
                sorted_literals = tuple(
                    sorted(map(orjson.dumps, clause.literals))
                )
                if sorted_literals not in self._state_set:
                    self.state[clause.label] = dataclasses.replace(
                        clause, birth_step=birth_step, processed=False
                    )
                    self._state_set.add(sorted_literals)

    def _do_deductions(self, given_clause_label: str) -> None:
        given_clause = self.state[given_clause_label]
        unprocessed_clauses = tuple(
            clause for clause in self.state.values() if clause.processed
        )
        self._add_to_state(
            all_possible_resolvents(
                unprocessed_clauses,
                given_clause,
            )
        )
        self._add_to_state(
            all_paramodulants_from_list(
                unprocessed_clauses,
                given_clause,
            )
        )
        self._add_to_state(
            all_possible_factors(
                given_clause,
            )
        )
        self._add_to_state(
            all_possible_reflexivity_resolvents(
                given_clause,
            )
        )
        self.state[given_clause_label] = dataclasses.replace(
            given_clause, processed=True
        )

    @property
    def proof_found(self) -> bool:
        """Return whether there is an empty clause in the state."""
        return any(clause.literals == () for clause in self.state.values())

    def proof_attempt(self) -> None:
        """Try finding a proof."""
        raise NotImplementedError  # pragma: no cover

    def _step(self, label: str) -> None:
        """
        Run one step of the given clause algorithm.

        :param label: given clause label
        """
        if (
            not self.state[label].processed
            and not self.proof_found
            and not min(
                False if clause.processed is None else clause.processed
                for clause in self.state.values()
            )
        ):
            self._do_deductions(label)

    @property
    def _last_birth_step(self) -> int:
        """Return the last birth step number of clauses in the proof state."""
        return max(getattr(clause, "birth_step", 0) for clause in self.state)
