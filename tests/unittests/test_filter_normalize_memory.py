import pytest
import sys

sys.path.append("./filter_plugins")
sys.path.append("../filter_plugins")
sys.path.append("../../filter_plugins")

from filters import FilterModule


@pytest.fixture
def data_oneos5():
    data = {
        "BOOT_SIZE": "1 024",
        "FLASH_SIZE": "65 536",
        "RAM": "262 144",
        "USER_PARTITION_FREE": "33 512",
        "USER_PARTITION_TOTAL": "64 688",
        "USER_PARTITION_USED": "31 176",
    }
    return data


@pytest.fixture
def data_oneos6():
    data = {
        "BOOT_SIZE": "100.0MiB",
        "FLASH_SIZE": "512.0MiB",
        "RAM": "1.0GiB",
        "USER_PARTITION_FREE": "85.4MiB",
        "USER_PARTITION_TOTAL": "366.9MiB",
        "USER_PARTITION_USED": "76.7%",
    }
    return data


def test_oneos5_kb(data_oneos5):
    expected_result = {
        "BOOT_SIZE": 1024,
        "FLASH_SIZE": 65536,
        "RAM": 262144,
        "USER_PARTITION_FREE": 33512,
        "USER_PARTITION_TOTAL": 64688,
        "USER_PARTITION_USED": 31176,
    }

    fm = FilterModule()
    result = fm.normalize_memory(data_oneos5)
    assert result == expected_result


def test_oneos5_b(data_oneos5):
    expected_result = {
        "BOOT_SIZE": 1048576,
        "FLASH_SIZE": 67108864,
        "RAM": 268435456,
        "USER_PARTITION_FREE": 34316288,
        "USER_PARTITION_TOTAL": 66240512,
        "USER_PARTITION_USED": 31924224,
    }

    fm = FilterModule()
    result = fm.normalize_memory(data_oneos5, unit="b")
    assert result == expected_result


def test_oneos5_mb(data_oneos5):
    expected_result = {
        "BOOT_SIZE": 1,
        "FLASH_SIZE": 64,
        "RAM": 256,
        "USER_PARTITION_FREE": 33,
        "USER_PARTITION_TOTAL": 64,
        "USER_PARTITION_USED": 31,
    }

    fm = FilterModule()
    result = fm.normalize_memory(data_oneos5, unit="mb")
    assert result == expected_result


def test_oneos6_kb(data_oneos6):
    expected_result = {
        "BOOT_SIZE": 102400,
        "FLASH_SIZE": 524288,
        "RAM": 1048576,
        "USER_PARTITION_FREE": 87450,
        "USER_PARTITION_TOTAL": 375706,
        "USER_PARTITION_USED": 288256,
    }

    fm = FilterModule()
    result = fm.normalize_memory(data_oneos6)
    assert result == expected_result


def test_oneos6_b(data_oneos6):
    expected_result = {
        "BOOT_SIZE": 104857600,
        "FLASH_SIZE": 536870912,
        "RAM": 1073741824,
        "USER_PARTITION_FREE": 89548391,
        "USER_PARTITION_TOTAL": 384722535,
        "USER_PARTITION_USED": 295174144,
    }

    fm = FilterModule()
    result = fm.normalize_memory(data_oneos6, unit="b")
    assert result == expected_result


def test_oneos6_mb(data_oneos6):
    expected_result = {
        "BOOT_SIZE": 100,
        "FLASH_SIZE": 512,
        "RAM": 1024,
        "USER_PARTITION_FREE": 86,
        "USER_PARTITION_TOTAL": 367,
        "USER_PARTITION_USED": 281,
    }

    fm = FilterModule()
    result = fm.normalize_memory(data_oneos6, unit="mb")
    assert result == expected_result
