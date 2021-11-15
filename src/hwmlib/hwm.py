from __future__ import annotations

from datetime import datetime, date, timedelta
from logging import getLogger
from time import mktime
from typing import Any, Mapping
from re import sub, MULTILINE, UNICODE
from decimal import Decimal

UNDEFINED = object()
DEFAULT_DATETIME = datetime.utcfromtimestamp(0)

log = getLogger(__name__)


class HWM:
    """
    Class for work with HWM.
    Possible types HWM values:
    str, timestamp, date, datetime, int, float.
    """
    value_type_dispatch_table = {
        'string': str,
        'timestamp': datetime,
        'datetime': datetime,
        'date': datetime,
        'int': int,
        'float': float,
    }

    def __init__(
        self,
        hwm_name: str,
        process_name: str,
        dataset_qualified_name: str = '',
        value: str = '',
        value_type: str = 'string',
        casted_value: any = UNDEFINED,
        modified_time: datetime = None,
        description: str = '',
    ) -> None:
        """
        Create an instance HWM.
        Mathematical operations like addition, subtraction and comparison are allowed.

        :param hwm_name: name
        :type hwm_name: str
        :param process_name: process name
        :type process_name: str
        :param dataset_qualified_name: dataset name
        :type dataset_qualified_name: str
        :param value: HWM value
        :type value: str
        :param value_type: HWM type
        :type value_type: str
        :param casted_value: casted value HWM
        :type casted_value: any
        :param modified_time: now by default
        :type modified_time: Optional[datetime]
        :param description: text field for description
        :type description: str

        **Example:**

        Create HWM.

        .. code:: python

            hwm = HWM(
                hwm_name='hwm_name',
                process_name='process',
                dataset_qualified_name='dataset_name',
                value='2020-01-01T00:00:00',
                value_type='datetime',
            )

        Mathematical operations:

        .. code:: python

            hwm - 1  #(result == december 31 2019)

            hwm - timedelta(377)
        """
        self.hwm_name = hwm_name
        self.process_name = process_name
        self.dataset_qualified_name = dataset_qualified_name
        self.value = value
        self.value_type = value_type
        self.casted_value = casted_value
        self.modified_time = modified_time or datetime.utcnow()
        self.description = description

        if not isinstance(value, str):
            raise TypeError('HWM value should be a string; use from_raw_value() instead.')

        if self.casted_value is UNDEFINED:
            self.casted_value = self.cast_value_from_string()

        if isinstance(self.casted_value, (datetime, date)):
            self.init_value = DEFAULT_DATETIME
        elif isinstance(self.casted_value, str):
            self.init_value = ''
        else:
            self.init_value = self.casted_value.__class__(1)

    def __add__(self, other) -> HWM:
        return self.__class__.from_raw_value(
            hwm_name=self.hwm_name,
            process_name=self.process_name,
            dataset_qualified_name=self.dataset_qualified_name,
            value=self.casted_value + self._casted_value_from_other(other),
            modified_time=None,
            description=self.description,
        )

    def __sub__(self, other) -> HWM:
        return self.__class__.from_raw_value(
            hwm_name=self.hwm_name,
            process_name=self.process_name,
            dataset_qualified_name=self.dataset_qualified_name,
            value=self.casted_value - self._casted_value_from_other(other),
            modified_time=None,
            description=self.description,
        )

    def __eq__(self, other) -> bool:
        return self.casted_value == self._casted_value_from_other(other)

    def __lt__(self, other) -> bool:
        return self.casted_value < self._casted_value_from_other(other)

    def __le__(self, other) -> bool:
        return self.casted_value <= self._casted_value_from_other(other)

    def __gt__(self, other) -> bool:
        return self.casted_value > self._casted_value_from_other(other)

    def __ge__(self, other) -> bool:
        return self.casted_value >= self._casted_value_from_other(other)

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('  # noqa: WPS221
            f'{repr(self.hwm_name)}, '
            f'{repr(self.process_name)}, '
            f'dataset_qualified_name={repr(self.dataset_qualified_name)}, '
            f'value={repr(self.value)}, '
            f'value_type={repr(self.value_type)}, '
            f'modified_time={repr(self.modified_time)}, '
            f'description={repr(self.description)}, '
            ')'
        )

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def escape_sql(s):
        return sub(r"([^\\])'", r"\1\'", s, flags=MULTILINE | UNICODE)

    @property
    def name(self) -> str:
        """
        Representation name.

        :return: name HWM
        :rtype: str
        """
        return f'{self.hwm_name}@{self.process_name}'

    @property
    def qualified_name(self) -> str:
        """
        Unique name HWM. Use for searching HWM in Atlas.

        :return: unique name HWM
        :rtype: str
        """
        return f'{self.name}@{self.dataset_qualified_name}'.rstrip('@')

    @classmethod
    def from_raw_value(
        cls,
        hwm_name: str,
        process_name: str,
        dataset_qualified_name: str = '',
        value: Any = None,
        modified_time: datetime = None,
        description: str = '',
    ) -> HWM:
        """
        Create HWM from different types of value.

        HWM is stored in strings in Atlas. The method cast value to str and detect type HWM.
        """
        casted_value = value

        if isinstance(casted_value, datetime):
            value = casted_value.isoformat()
            value_type = 'datetime'
        elif isinstance(casted_value, date):
            value = casted_value.isoformat()
            value_type = 'date'
        elif isinstance(casted_value, int):
            value = str(casted_value)
            value_type = 'int'
        elif isinstance(casted_value, (float, Decimal)):
            value = str(float(casted_value))
            value_type = 'float'
        elif isinstance(casted_value, str):
            value_type = 'string'
            log.warning("HWM's value type - string")
        else:
            raise TypeError(f'Cannot cast "{value}".')

        return cls(
            hwm_name=hwm_name,
            process_name=process_name,
            dataset_qualified_name=dataset_qualified_name,
            value=value,
            value_type=value_type,
            modified_time=modified_time,
            description=description,
            casted_value=casted_value,
        )

    @classmethod
    def from_atlas_spec(cls, data: Mapping, dataset_qualified_name: str = '') -> HWM:
        """
        Create HWM from dict of attributes like stored in Atlas.
        """
        modified_time = data.get('modifiedTime')
        if modified_time:
            modified_time = datetime.fromtimestamp(modified_time)

        return cls(
            data['hwmName'],
            data['processName'],
            dataset_qualified_name=data.get('datasetQualifiedName') or dataset_qualified_name,
            value=data.get('value') or '',
            value_type=data.get('type') or 'string',
            description=data.get('description') or '',
            modified_time=modified_time,
        )

    def to_atlas_spec(self) -> dict:
        """
        Return HWM attributes in Atlas format.

        :return: dict of attributes HWM
        :rtype: dict
        """
        return {
            'name': self.name,
            'hwmName': self.hwm_name,
            'qualifiedName': self.qualified_name,
            'processName': self.process_name,
            'datasetQualifiedName': self.dataset_qualified_name,
            'value': self.value,
            'type': self.value_type,
            'description': self.description,
            'modifiedTime': mktime(self.modified_time.timetuple()),
        }

    def copy(self):
        return self.from_atlas_spec(self.to_atlas_spec())

    def cast_value_from_string(self) -> Any:
        """
        Cast value to Python type from string.
        """
        if not self.value_type or self.value_type == 'string':
            return self.value

        if self.value_type and self.value_type not in self.value_type_dispatch_table:
            raise TypeError(
                f'Not supported type {self.value_type}. '
                f'Available: {list(self.value_type_dispatch_table.keys())}.',
            )

        func = self.value_type_dispatch_table.get(self.value_type)
        if self.value_type in {'timestamp', 'datetime'}:
            result = datetime.fromisoformat(self.value)
        elif self.value_type == 'date':
            result = func.strptime(self.value, '%Y-%m-%d').date()
        else:
            result = func(self.value)

        return result

    def _casted_value_from_other(self, other: Any) -> Any:
        """
        Cast value to Python type for comparison and math operations with HWM.

        :param other: value used for comparison or math operations
        :type other: Any
        """
        value = other
        if isinstance(other, self.__class__):
            value = other.casted_value
        if (
            not isinstance(other, (self.__class__, datetime, date, timedelta))
            and self.value_type in {'timestamp', 'datetime'}
        ):
            value = timedelta(seconds=other)
        elif (
            not isinstance(other, (self.__class__, datetime, date, timedelta))
            and self.value_type == 'date'
        ):
            value = timedelta(days=other)
        return value
