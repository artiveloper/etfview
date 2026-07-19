from etf_collector.infra.kis.master_file import _PART2_LEN, _PART2_OFFSETS, parse_master_file


def _build_part2(
    group_code: str = "EF", listed_date: str = "20021014", listed_shares: str = "223650"
) -> str:
    chars = ["0"] * _PART2_LEN

    def place(field: str, value: str, *, ljust: bool = False) -> None:
        start, end = _PART2_OFFSETS[field]
        width = end - start
        text = value.ljust(width) if ljust else value.rjust(width, "0")
        chars[start:end] = list(text[:width])

    place("group_code", group_code, ljust=True)
    place("listed_date", listed_date)
    place("listed_shares", listed_shares)
    return "".join(chars)


def _build_line(short_code: str, standard_code: str, name: str, part2: str) -> str:
    part1 = f"{short_code:<9}{standard_code:<12}{name}"
    return part1 + part2


def test_parse_line_extracts_etf_row() -> None:
    part2 = _build_part2()
    line = _build_line("069500", "KR7069500007", "KODEX 200", part2)

    rows = parse_master_file(line.encode("cp949"))

    assert len(rows) == 1
    etf = rows[0]
    assert etf.short_code == "069500"
    assert etf.standard_code == "KR7069500007"
    assert etf.name == "KODEX 200"
    assert etf.listed_date.isoformat() == "2002-10-14"
    assert etf.listed_shares == 223650


def test_parse_line_filters_out_non_etf_rows() -> None:
    part2 = _build_part2(group_code="ST")
    line = _build_line("005930", "KR7005930003", "Samsung Electronics", part2)

    rows = parse_master_file(line.encode("cp949"))

    assert rows == []


def test_parse_master_file_skips_blank_lines() -> None:
    part2 = _build_part2()
    line = _build_line("069500", "KR7069500007", "KODEX 200", part2)
    content = f"\n{line}\n\n".encode("cp949")

    rows = parse_master_file(content)

    assert len(rows) == 1
