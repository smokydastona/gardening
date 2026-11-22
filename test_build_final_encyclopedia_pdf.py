from pathlib import Path

from build_final_encyclopedia_pdf import OUTPUT_MD, SOURCE_FILES, compile_markdown, load_sections


def test_compiled_encyclopedia_includes_core_handbook(tmp_path: Path) -> None:
    for _title, file_name, _deck in SOURCE_FILES:
        (tmp_path / file_name).write_text(f"Content from {file_name}.", encoding="utf-8")

    sections = load_sections(tmp_path)
    compiled = compile_markdown(tmp_path, sections)

    assert "# Core Handbook" in compiled
    assert "Content from ERRINGTON_GARDENING_ENCYCLOPEDIA_MANUSCRIPT.md." in compiled
    assert (tmp_path / OUTPUT_MD).read_text(encoding="utf-8") == compiled
