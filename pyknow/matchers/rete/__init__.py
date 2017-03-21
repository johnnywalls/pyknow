"""
RETE algorithm implementation.

This is implemented as described by Charles L. Forgy in his original
Ph.D thesis paper_. With minor changes to allow CLIPS like matching and
a more pythonic approach.

.. _paper: http://reports-archive.adm.cs.cmu.edu/anon/scan/CMU-CS-79-forgy.pdf

"""
from functools import lru_cache
from itertools import chain
from collections import Counter

from pyknow import OR
from .nodes import BusNode, ConflictSetNode, FeatureTesterNode
from .utils import prepare_rule, extract_facts, generate_checks, wire_rule
from pyknow.abstract import Matcher


class ReteMatcher(Matcher):
    """RETE algorithm with `pyknow` matcher interface."""

    def __init__(self, *args, **kwargs):
        """Create the RETE network for `self.engine`."""
        super().__init__(*args, **kwargs)
        self.root_node = BusNode()
        self.build_network()

    @lru_cache(maxsize=1)
    def _get_conflict_set_nodes(self):
        def _get_csn(node):
            if isinstance(node, ConflictSetNode):
                yield node
            for child in node.children:
                yield from _get_csn(child.node)

        return set(_get_csn(self.root_node))

    def changes(self, adding=None, deleting=None):
        """Pass the given changes to the root_node."""
        if adding is not None:
            for added in adding:
                self.root_node.add(added)
        if deleting is not None:
            for deleted in deleting:
                self.root_node.remove(deleted)

        activations = []
        for csn in self._get_conflict_set_nodes():
            activations += csn.get_activations()
        return activations

    def build_network(self):
        ruleset = self.prepare_ruleset(self.engine)
        alpha_terminals = self.build_alpha_part(ruleset, self.root_node)
        self.build_beta_part(ruleset, alpha_terminals)

    @staticmethod
    def prepare_ruleset(engine):
        """
        Given a `KnowledgeEngine`, generate a set of rules suitable for
        RETE network generation.

        """
        return {prepare_rule(rule) for rule in engine.get_rules()}

    @staticmethod
    def build_alpha_part(ruleset, root_node):
        """
        Given a set of already adapted rules, build the alpha part of
        the RETE network starting at `root_node`.

        """
        # Generate a dictionary with rules and the set of facts of the
        # rule.
        rule_facts = {rule: extract_facts(rule) for rule in ruleset}

        # For each fact build a list of checker function capable of
        # check for each part in the fact.
        fact_checks = {fact: set(generate_checks(fact))
                       for fact in chain.from_iterable(rule_facts.values())}

        # Make a ranking of the most used checks
        check_rank = Counter(chain.from_iterable(fact_checks.values()))

        def weighted_check_sort(rule):
            """Sort rules by the average weight of its checks."""
            total = 0
            for fact in rule_facts[rule]:
                for check in fact_checks[fact]:
                    total += check_rank[check]
            return total / len(rule_facts[rule])

        sorted_rules = sorted(ruleset, key=weighted_check_sort, reverse=True)

        # For rule in rank order and for each rule fact also in rank
        # order, build the alpha brank looking for an existing node
        # first.
        fact_terminal_nodes = dict()
        for rule in sorted_rules:
            for fact in rule_facts[rule]:
                current_node = root_node
                fact_sorted_checks = sorted(
                    fact_checks[fact],
                    key=lambda c: check_rank[c],
                    reverse=True)

                for check in fact_sorted_checks:
                    # Look for a child node with the given check in the
                    # current parent node.
                    for child in current_node.children:
                        if child.node.matcher is check:
                            current_node = child.node
                            break
                    else:
                        # Create a new node and append as child
                        new_node = FeatureTesterNode(check)
                        current_node.add_child(new_node, new_node.activate)
                        current_node = new_node

                fact_terminal_nodes[fact] = current_node

        # Return this dictionary containing the last alpha node for each
        # fact.
        return fact_terminal_nodes

    @staticmethod
    def build_beta_part(ruleset, alpha_terminals):
        """
        Given a set of already adapted rules, and a dictionary of
        patterns and alpha_nodes, wire up the beta part of the RETE
        network.

        """
        for rule in ruleset:
            if isinstance(rule[0], OR):
                for subrule in rule[0]:
                    wire_rule(rule, alpha_terminals, lhs=subrule)
            else:
                wire_rule(rule, alpha_terminals, lhs=rule)

    def print_network(self):
        """
        Generate a graphviz compatible graph.

        """
        def gen_edges(node):
            name = str(id(node))

            yield '{name} [label="{cls_name}: {content}"];'.format(
                name=name,
                cls_name=node.__class__.__name__,
                content=repr(node))

            for child in node.children:
                yield '{parent} -> {child} [label={child_label}];'.format(
                    parent=name,
                    child=str(id(child.node)),
                    child_label=child.callback)
                yield from gen_edges(child.node)

        return "digraph {\n %s \n}" % ("\n".join(
            gen_edges(self.root_node)))
