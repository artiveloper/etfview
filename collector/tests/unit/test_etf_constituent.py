import pytest

from etf_collector.infra.kis.etf_constituent import map_to_domain, parse_constituent_master


def test_parse_constituent_master_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        parse_constituent_master(b"")


def test_map_to_domain_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        map_to_domain([])
