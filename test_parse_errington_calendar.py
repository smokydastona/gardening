from parse_errington_calendar import extract_plant_and_remainder, parse_row_columns, parse_section_rows


def test_extract_plant_and_remainder_week_pattern() -> None:
    plant, remainder = extract_plant_and_remainder("Rosemary Wk 3–4 (under lights) — —")
    assert plant == "Rosemary"
    assert remainder.startswith("Wk 3–4")


def test_parse_row_columns_direct_sow() -> None:
    plant, indoor, direct, action = parse_row_columns("Sweet Peas — Direct sow outdoors 🌿 Wk 3–4 —")
    assert plant == "Sweet Peas"
    assert indoor == ""
    assert direct == "Direct sow outdoors 🌿 Wk 3–4"
    assert action == ""


def test_parse_row_columns_multi_line_group() -> None:
    row = "Apple / Pear / Plum / Cherry — — ✄ Prune dormant trees Jan–Feb"
    plant, indoor, direct, action = parse_row_columns(row)
    assert plant == "Apple / Pear / Plum / Cherry"
    assert indoor == ""
    assert direct == ""
    assert "Prune dormant trees" in action


def test_parse_section_rows_groups_multiline_entry() -> None:
    lines = [
        "Apple / Pear / Plum /",
        "Cherry",
        "— — ✄ Prune dormant trees",
        "Jan–Feb",
        "Bare-root fruit stock — — Order from nursery now",
    ]
    rows = parse_section_rows(lines)
    assert rows[0] == "Apple / Pear / Plum / Cherry — — ✄ Prune dormant trees Jan–Feb"
    assert rows[1] == "Bare-root fruit stock — — Order from nursery now"