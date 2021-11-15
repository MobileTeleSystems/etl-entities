from pytest import mark, raises

from datetime import datetime, date, timedelta
from decimal import Decimal
from unittest.mock import patch

from hwmlib.hwm import HWM


class TestHWM:
    def test_hwm_sum(self):
        hwm1 = HWM(
            hwm_name='my_awesome_hwm',
            process_name='process_name',
            dataset_qualified_name='source',
            value='100',
            value_type='int',
        )
        hwm2 = HWM(
            hwm_name='my_awesome_hwm2',
            process_name='process_name',
            dataset_qualified_name='source',
            value='200',
            value_type='int',
        )
        hwm = hwm1 + hwm2
        assert hwm.value == '300'
        assert hwm.casted_value == 300
        assert hwm.init_value == 1
        assert hwm.hwm_name == 'my_awesome_hwm'

    def test_hwm_eq(self):

        hwm1 = HWM(
            hwm_name='my_awesome_hwm',
            process_name='process_name',
            dataset_qualified_name='dataset_qn',
            value='100',
            value_type='int',
            modified_time=datetime(2050, 11, 22),
        )
        hwm2 = HWM.from_raw_value(
            hwm_name='my_awesome_hwm2',
            process_name='process_name',
            dataset_qualified_name='dataset_qn',
            value=200,
        )
        params = (
            'my_awesome_hwm',
            'process_name',
            'dataset_qn',
            '100',
            'int',
            'datetime.datetime(2050, 11, 22, 0, 0)',
        )
        for param in params:
            assert param in repr(hwm1)

        assert str(hwm1) == 'my_awesome_hwm@process_name'
        assert hwm1 < hwm2
        assert hwm1 <= hwm2
        assert hwm2 > hwm1
        assert hwm2 >= hwm1
        assert hwm1 != hwm2

    def test_hwm_qualified_name(self):
        hwm = HWM(
            hwm_name='hwm_name_test',
            process_name='process_name',
            dataset_qualified_name='schema.table',
            value='2021-08-30',
        )
        assert hwm.qualified_name == 'hwm_name_test@process_name@schema.table'
        assert hwm.value == '2021-08-30'

    def test_check_datetime_hwm(self):
        hwm = HWM(
            hwm_name='my',
            process_name='awesome',
            dataset_qualified_name='hwm',
            value='2020-01-01T00:00:00',
            value_type='datetime',
        )

        hwm = hwm - 1
        assert hwm.casted_value.year == 2019
        assert hwm.casted_value.day == 31
        hwm = hwm - timedelta(377)
        assert hwm.casted_value.year == 2018
        assert hwm.casted_value.day == 19

    def test_check_date_hwm(self):
        hwm = HWM(
            hwm_name='my',
            process_name='awesome',
            dataset_qualified_name='hwm',
            value='2020-05-27',
            value_type='date',
        )

        hwm = hwm - 1
        assert hwm.casted_value.year == 2020
        assert hwm.casted_value.day == 26
        hwm = hwm - timedelta(1)
        assert hwm.casted_value.day == 25

    def test_hwm_modified_time(self):
        class NewDate:
            @staticmethod
            def utcnow():
                return datetime(2021, 11, 12)

        with patch('hwmlib.hwm.datetime', NewDate):
            hwm = HWM(
                hwm_name='my',
                process_name='awesome',
                dataset_qualified_name='hwm',
                value='2020-01-01',
                value_type='date',
                casted_value=date(2020, 1, 1),
            )

        assert hwm.casted_value == date(2020, 1, 1)
        assert hwm.modified_time == datetime(2021, 11, 12)

    def test_hwm_str_type(self):
        with raises(TypeError) as e:
            HWM(
                hwm_name='my',
                process_name='awesome',
                dataset_name='hwm',
                value=200,
            )
            assert str(e.value) == 'HWM value should be a string; use from_raw_value() instead.'

    def test_hwm_unsupported_type(self):
        with raises(TypeError) as e:
            HWM(
                hwm_name='my',
                process_name='awesome',
                dataset_name='hwm',
                value='2020-01-01',
                value_type='set',
            )
            assert str(e.value) == (
                'Not supported type set.'
                'Available: ["string", "timestamp", "datetime", "date", "int", "float"].'
            )

    @mark.parametrize('casted_value', [2.0, date(2020, 3, 22), Decimal(100.0)], ids=['float', 'date', 'Decimal'])
    def test_from_raw_value_casted_value(self, casted_value):
        process_name = 'etl_crawler_msk'
        source = 'dataset1'

        hwm = HWM.from_raw_value(
            hwm_name='my_awesome_hwm',
            process_name=process_name,
            dataset_qualified_name=source,
            value=casted_value,
        )

        assert hwm.casted_value == casted_value

    def test_to_atlas_spec_and_from(self):
        hwm = HWM(
            hwm_name='test_hwm',
            process_name='test_process',
            dataset_qualified_name='test_dataset',
            value='9999999',
            value_type='int',
        )
        hwm_dict = hwm.to_atlas_spec()
        got_hwm = HWM.from_atlas_spec(hwm_dict)
        assert hwm == got_hwm

    def test_copy_hwm(self):
        hwm = HWM(
            hwm_name='test_hwm',
            process_name='test_process',
            dataset_qualified_name='test_dataset',
            value='9999999',
            value_type='int',
        )
        hwm_copy = hwm.copy()
        assert hwm == hwm_copy

    def test_not_str_hwm(self):
        with raises(TypeError):
            HWM(
                hwm_name='test_hwm',
                process_name='test_process',
                dataset_qualified_name='test_dataset',
                value=1,
                value_type='int',
            )

    def test_incorrect_value_type(self):
        with raises(TypeError):
            HWM(
                hwm_name='test_hwm',
                process_name='test_process',
                dataset_qualified_name='test_dataset',
                value='(1, 2)',
                value_type='frozenset',
            )

    def test_from_raw_value_string_value(self):
        value = 'some string value'
        hwm = HWM.from_raw_value(
            hwm_name='from_raw_value_hwm',
            process_name='process',
            dataset_qualified_name='dataset_qn',
            value=value,
        )
        assert hwm.value == value
