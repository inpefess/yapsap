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
Factoring
==========
"""
from typing import Tuple

from tptp_lark_parser import grammar as gram

from yapsap.unification import NonUnifiableError, most_general_unifier


def factoring(
    given_clause: gram.Clause,
    literal_one: gram.Literal,
    literal_two: gram.Literal,
) -> gram.Clause:
    r"""
    Apply positive factoring rule.

    .. _factoring:

    .. math:: {\frac{C\vee A_1\vee A_2}{\sigma\left(C\vee L_1\right)}}

    where

    * :math:`C` and is a clause
    * :math:`A_1` and :math:`A_2` are atomic formulae (positive literals)
    * :math:`\sigma` is a most general unifier of :math:`A_1` and :math:`A_2`

    >>> from tptp_lark_parser.grammar import Predicate, Variable, Function
    >>> from pprint import pprint
    >>> pprint(factoring(
    ...     gram.Clause((gram.Literal(True, Predicate(8, (Variable(0),))),)),
    ...     gram.Literal(False, Predicate(9, (Variable(0),))),
    ...     gram.Literal(False, Predicate(9, (Function(0, ()),)))
    ... ).literals, width=75)
    (Literal(negated=True,
             atom=Predicate(index=8,
                            arguments=(Function(index=0, arguments=()),))),
     Literal(negated=False,
             atom=Predicate(index=9,
                            arguments=(Function(index=0, arguments=()),))))
    >>> factoring(
    ...     gram.Clause(()), gram.Literal(False, Predicate(8, ())),
    ...     gram.Literal(True, Predicate(7, ()))
    ... )
    Traceback (most recent call last):
     ...
    ValueError: factoring is not possible for Literal(negated=False, atom=P...

    :param given_clause: :math:`C`
    :param literal_one: :math:`A_1`
    :param literal_two: :math:`A_2`
    :returns: a new clause --- the factoring result
    :raises ValueError: if ``literal_one`` or ``literal_two`` is negated
    """
    if literal_one.negated or literal_two.negated:
        raise ValueError(
            f"factoring is not possible for {literal_one} and {literal_two}"
        )
    substitutions = most_general_unifier((literal_one.atom, literal_two.atom))
    new_literals = given_clause.literals + (literal_one,)
    result = gram.Clause(new_literals)
    for substitution in substitutions:
        result = substitution.substitute_in_clause(result)
    return result


def all_possible_factors(
    given_clause: gram.Clause,
) -> Tuple[gram.Clause, ...]:
    """
    One of the four basic building blocks of the Given Clause algorithm.

    >>> from tptp_lark_parser.tptp_parser import TPTPParser
    >>> parser = TPTPParser()
    >>> clause = parser.parse("cnf(one, axiom, p(c) | p(X) | q).")[0]
    >>> tuple(map(
    ...     parser.cnf_parser.pretty_print,
    ...     all_possible_factors(clause)
    ... ))
    ('cnf(x..., lemma, q() | p(c), inference(factoring, [], [one])).',)

    :param given_clause: a new clause which should be combined with all the
        processed ones
    :returns: results of all possible factors with each one from
        ``clauses`` and the ``given_clause``
    """
    factors: Tuple[gram.Clause, ...] = ()
    for i, literal_one in enumerate(given_clause.literals):
        for j in range(i + 1, len(given_clause.literals)):
            if (
                not literal_one.negated
                and not given_clause.literals[j].negated
            ):
                a_clause = gram.Clause(
                    given_clause.literals[:i]
                    + given_clause.literals[i + 1 : j]
                    + given_clause.literals[j + 1 :]
                )
                try:
                    factors = factors + (
                        factoring(
                            a_clause, literal_one, given_clause.literals[j]
                        ),
                    )
                except NonUnifiableError:
                    pass
    return tuple(
        gram.Clause(
            literals=factor.literals,
            inference_parents=(given_clause.label,),
            inference_rule="factoring",
        )
        for factor in factors
    )
