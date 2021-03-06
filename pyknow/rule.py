from collections.abc import Callable, Iterable
from functools import update_wrapper, partial, lru_cache
from itertools import chain

from pyknow import watchers


class ConditionalElement(tuple):
    """Base Conditional Element"""

    def __new__(cls, *args):
        return super(ConditionalElement, cls).__new__(cls, args)

    def __repr__(self):
        return "%s%s" % (self.__class__.__name__, super().__repr__())


class Rule(ConditionalElement):
    """
    Base ``CE``, all ``CE`` are to derive from this class.

    This class is used as a decorator, thus provoking __call__
    to be called twice:

    #. The first call is when the decorator is been created. At this
       point we assign the function decorated to ``self._wrapped`` and
       return ``self`` to be called the second time.

    #. The second call is to execute the decorated function, se we
       pass all the arguments along.
    """

    def __new__(cls, *args, salience=0, where=None):
        obj = super(Rule, cls).__new__(cls, *args)

        obj._wrapped = None
        obj._wrapped_self = None
        obj.salience = salience

        if where is None:
            where = list()
        elif not isinstance(where, Iterable):
            where = [where]
        obj.where = where

        return obj

    def new_conditions(self, *args):
        """
        Generate a new rule with the same attributes but with the given
        conditions.

        """
        obj = self.__class__(*args, salience=self.salience, where=self.where)

        if self._wrapped:
            obj = obj(self._wrapped)

        return obj

    def __hash__(self):
        return hash(tuple(self)
                    + (self._wrapped, self._wrapped_self, self.salience))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            self_data = tuple(self) + (self._wrapped,
                                       self._wrapped_self,
                                       self.salience)
            other_data = tuple(other) + (other._wrapped,
                                         other._wrapped_self,
                                         other.salience)
            return self_data == other_data
        else:
            return False

    def __call__(self, *args, **kwargs):
        """
        Make method checks if it's the first call, and update wrapper.
        Othersise execute the RHS.
        """
        if self._wrapped is None:
            if not args:
                raise AttributeError("Mandatory function not provided.")
            else:
                self._wrapped = args[0]
                return update_wrapper(self, self._wrapped)
        elif self._wrapped_self is None:
            return self._wrapped(*args, **kwargs)
        else:
            return self._wrapped(self._wrapped_self, *args, **kwargs)

    def __repr__(self):
        return "%s => %r" % (super().__repr__(), self._wrapped)

    def __get__(self, instance, owner):
        self._wrapped_self = instance
        return self


class Bindable:
    def __rlshift__(self, other):
        if not isinstance(other, str):
            raise TypeError("%s can only be binded to a string" % self)
        elif self.__bind__ is not None:
            raise RuntimeError("%s can only be binded once" % self)
        else:
            self.__bind__ = other
            return self


class ComposableCE:
    def __and__(self, other):
        if isinstance(self, AND) and isinstance(other, AND):
            return AND(*[x for x in chain(self, other)])
        elif isinstance(self, AND):
            return AND(*[x for x in self]+[other])
        elif isinstance(other, AND):
            return AND(*[self]+[x for x in other])
        else:
            return AND(self, other)

    def __or__(self, other):
        if isinstance(self, OR) and isinstance(other, OR):
            return OR(*[x for x in chain(self, other)])
        elif isinstance(self, OR):
            return OR(*[x for x in self]+[other])
        elif isinstance(other, OR):
            return OR(*[self]+[x for x in other])
        else:
            return OR(self, other)

    def __invert__(self):
        return NOT(self)


class AND(ComposableCE, ConditionalElement):
    pass


class OR(ComposableCE, ConditionalElement):
    pass


class NOT(ComposableCE, ConditionalElement):
    pass


class ComposablePCE:
    def __and__(self, other):
        if isinstance(self, ANDPCE) and isinstance(other, ANDPCE):
            return ANDPCE(*[x for x in chain(self, other)])
        elif isinstance(self, ANDPCE):
            return ANDPCE(*[x for x in self]+[other])
        elif isinstance(other, ANDPCE):
            return ANDPCE(*[self]+[x for x in other])
        else:
            return ANDPCE(self, other)

    def __or__(self, other):
        if isinstance(self, ORPCE) and isinstance(other, ORPCE):
            return ORPCE(*[x for x in chain(self, other)])
        elif isinstance(self, ORPCE):
            return ORPCE(*[x for x in self]+[other])
        elif isinstance(other, ORPCE):
            return ORPCE(*[self]+[x for x in other])
        else:
            return ORPCE(self, other)

    def __invert__(self):
        return NOTPCE(self)


class PatternConditionalElement(ComposablePCE, ConditionalElement):
    pass


class ANDPCE(PatternConditionalElement):
    pass


class ORPCE(PatternConditionalElement):
    pass


class NOTPCE(PatternConditionalElement):
    pass


class HasID:
    def __hash__(self):
        return hash((self.__bind__, ) + tuple(self))

    def __eq__(self, other):
        return (self.__class__ == other.__class__
                and self.__bind__ == other.__bind__
                and super().__eq__(other))


class LiteralPCE(HasID, Bindable, PatternConditionalElement):
    def __new__(cls, value, __bind__=None):
        obj = super(LiteralPCE, cls).__new__(cls, value)
        obj.__bind__ = __bind__
        return obj

    @property
    def value(self):
        return self[0]

    def __repr__(self):
        return "L(%r)" % self.value


class WildcardPCE(HasID, Bindable, PatternConditionalElement):
    def __new__(cls, __bind__=None):
        obj = super(WildcardPCE, cls).__new__(cls)
        obj.__bind__ = __bind__
        return obj

    def __repr__(self):
        return "W()" if self.__bind__ is None else "W(%r)" % self.__bind__


class PredicatePCE(HasID, Bindable, PatternConditionalElement):
    def __new__(cls, match, __bind__=None):
        if not isinstance(match, Callable):
            raise TypeError("PredicatePCE needs a callable.")
        else:
            obj = super(PredicatePCE, cls).__new__(cls, match)
            obj.__bind__ = __bind__
            return obj

    @property
    def match(self):
        return self[0]
