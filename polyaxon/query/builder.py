from collections import namedtuple
from typing import Any, Callable, Optional

from hestia.date_formatter import DateTimeFormatter, DateTimeFormatterException
from hestia.list_utils import to_list

from django.db.models import Q

from query.exceptions import QueryConditionException


class QueryCondSpec(namedtuple("QueryCondSpec", "cond params")):

    def items(self):
        return self._asdict().items()


class QueryBuilder(object):
    """The `QueryBuild` adds filters to a `QuerySet` from a `params` mapping.

    Filters are a mapping of <name: Condition>, Condition being an object that update the queryset.
    """

    def __init__(self, filters):
        self.filters = filters

    def build(self, queryset: Any, params: Any) -> Any:
        for name, condition in self.filters.items():
            if name in params:
                queryset = condition.apply(queryset, name, params[name])
        return queryset


class BaseCondition(object):
    """The base condition representing a single filter to apply to a `QuerySet`"""

    def apply(self, queryset, name, params):
        raise NotImplementedError


class BaseOperatorCondition(BaseCondition):

    def __init__(self, op: str, negation: bool = False) -> None:
        if op not in self.VALUES and op not in self.REPRESENTATIONS:
            raise QueryConditionException(
                'Received an invalid operator `{}`, '
                'possible values `{}` or `{}`.'.format(op, self.VALUES, self.REPRESENTATIONS))

        self.operator = self._get_operator(op, negation)

    def __eq__(self, other: 'BaseOperatorCondition') -> bool:
        return self.operator == other.operator

    def apply(self, queryset: Any, name: str, params: Any) -> Any:
        return queryset.filter(self.operator(name=name, params=params))


class CallbackCondition(BaseCondition):
    """The `CallbackCondition` represents a filter based on a callback to apply."""

    def __init__(self, callback: Callable) -> None:
        self.callback = callback
        self.negation = False

    def __call__(self, op, negation: bool = False) -> 'CallbackCondition':
        self.negation = negation
        return self

    def apply(self, queryset: Any, name: str, params: Any) -> Any:
        return self.callback(queryset, params, self.negation)


class EqualityCondition(BaseOperatorCondition):
    VALUES = {'eq', }
    REPRESENTATIONS = {'=', }
    REPRESENTATION_MAPPING = (
        ('=', 'eq'),
    )

    @classmethod
    def _get_operator(cls, op: str, negation: bool = False) -> Optional[Callable]:
        if op not in cls.VALUES and op not in cls.REPRESENTATIONS:
            return None

        if negation:
            return cls._neq_operator
        return cls._eq_operator

    @staticmethod
    def _eq_operator(name: str, params: Any) -> Any:
        return Q(**{name: params})

    @classmethod
    def _neq_operator(cls, name: str, params: Any) -> any:
        return ~cls._eq_operator(name, params)


class ComparisonCondition(EqualityCondition):
    VALUES = EqualityCondition.VALUES | {'lt', 'lte', 'gt', 'gte'}
    REPRESENTATIONS = EqualityCondition.REPRESENTATIONS | {'<', '<=', '>', '>='}
    REPRESENTATION_MAPPING = EqualityCondition.REPRESENTATION_MAPPING + (
        ('<', 'lt'),
        ('<=', 'lte'),
        ('>', 'gt'),
        ('>=', 'gte'),
    )

    @classmethod
    def _get_operator(cls, op: str, negation: bool = False) -> Optional[Callable]:
        if op not in cls.VALUES and op not in cls.REPRESENTATIONS:
            return None

        _op = EqualityCondition._get_operator(op, negation)
        if _op:
            return _op

        if op == 'lt' or op == '<':
            if negation:
                return cls._gte_operator
            return cls._lt_operator

        if op == 'lte' or op == '<=':
            if negation:
                return cls._gt_operator
            return cls._lte_operator

        if op == 'gt' or op == '>':
            if negation:
                return cls._lte_operator
            return cls._gt_operator

        if op == 'gte' or op == '>=':
            if negation:
                return cls._lt_operator
            return cls._gte_operator

    @staticmethod
    def _lt_operator(name: str, params: Any) -> Any:
        name = '{}__lt'.format(name)
        return Q(**{name: params})

    @staticmethod
    def _gt_operator(name: str, params: Any) -> Any:
        name = '{}__gt'.format(name)
        return Q(**{name: params})

    @staticmethod
    def _lte_operator(name: str, params: Any) -> Any:
        name = '{}__lte'.format(name)
        return Q(**{name: params})

    @staticmethod
    def _gte_operator(name: str, params: Any) -> Any:
        name = '{}__gte'.format(name)
        return Q(**{name: params})


class DateTimeCondition(ComparisonCondition):
    VALUES = ComparisonCondition.VALUES | {'range', }
    REPRESENTATIONS = ComparisonCondition.REPRESENTATIONS | {'..', }
    REPRESENTATION_MAPPING = ComparisonCondition.REPRESENTATION_MAPPING + (
        ('..', 'range'),
    )

    @classmethod
    def _get_operator(cls, op: str, negation: bool = False) -> Optional[Callable]:
        if op not in cls.VALUES and op not in cls.REPRESENTATIONS:
            return None

        _op = ComparisonCondition._get_operator(op, negation)
        if _op:
            return _op

        if negation:
            return cls._nrange_operator
        return cls._range_operator

    @staticmethod
    def _range_operator(name: str, params: Any) -> Any:
        assert len(params) == 2
        try:
            start_date = DateTimeFormatter.extract(params[0])
            end_date = DateTimeFormatter.extract(params[1])
        except DateTimeFormatterException as e:
            raise QueryConditionException(e)

        name = '{}__range'.format(name)
        return Q(**{name: (start_date, end_date)})

    @classmethod
    def _nrange_operator(cls, name: str, params: Any) -> Any:
        return ~cls._range_operator(name, params)


class ValueCondition(EqualityCondition):
    VALUES = EqualityCondition.VALUES | {'in', }
    REPRESENTATIONS = EqualityCondition.REPRESENTATIONS | {'|', }
    REPRESENTATION_MAPPING = EqualityCondition.REPRESENTATION_MAPPING + (
        ('|', 'in'),
    )

    @classmethod
    def _get_operator(cls, op: str, negation: bool = False) -> Any:
        if op not in cls.VALUES and op not in cls.REPRESENTATIONS:
            return None

        _op = EqualityCondition._get_operator(op, negation)
        if _op:
            return _op

        if negation:
            return cls._nin_operator
        return cls._in_operator

    @staticmethod
    def _in_operator(name: str, params: Any) -> Any:
        assert isinstance(params, (list, tuple))
        name = '{}__in'.format(name)
        return Q(**{name: params})

    @classmethod
    def _nin_operator(cls, name: str, params: Any) -> Any:
        return ~cls._in_operator(name, params)


class ArrayCondition(EqualityCondition):
    VALUES = EqualityCondition.VALUES | {'in', }
    REPRESENTATIONS = EqualityCondition.REPRESENTATIONS | {'|', }
    REPRESENTATION_MAPPING = EqualityCondition.REPRESENTATION_MAPPING + (
        ('|', 'in'),
    )

    @classmethod
    def _get_operator(cls, op: str, negation: bool = False) -> Optional[Callable]:
        if op not in cls.VALUES and op not in cls.REPRESENTATIONS:
            return None

        _op = cls._get_eq_operator(op, negation)
        if _op:
            return _op

        if negation:
            return cls._nin_operator
        return cls._in_operator

    @classmethod
    def _get_eq_operator(cls, op: str, negation: bool = False) -> Optional[Callable]:
        if op not in EqualityCondition.VALUES and op not in EqualityCondition.REPRESENTATIONS:
            return None

        if negation:
            return cls._neq_operator
        return cls._eq_operator

    @staticmethod
    def _eq_operator(name: str, params: Any) -> Any:
        name = '{}__contains'.format(name)
        return Q(**{name: to_list(params)})

    @staticmethod
    def _in_operator(name: str, params: Any) -> Any:
        assert isinstance(params, (list, tuple))
        name = '{}__overlap'.format(name)
        return Q(**{name: params})

    @classmethod
    def _nin_operator(cls, name: str, params: Any) -> Any:
        return ~cls._in_operator(name, params)
