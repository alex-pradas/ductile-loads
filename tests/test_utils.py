"""Tests for _sanitize_filename helper."""

from ductile_loads.loads import _sanitize_filename


class TestSanitizeFilename:
    def test_clean_string_unchanged(self):
        assert _sanitize_filename("hello_world") == "hello_world"

    def test_spaces_replaced(self):
        assert _sanitize_filename("hello world") == "hello_world"

    def test_special_chars_replaced(self):
        assert _sanitize_filename("file@name#1!") == "file_name_1"

    def test_consecutive_underscores_collapsed(self):
        assert _sanitize_filename("a___b") == "a_b"

    def test_leading_trailing_underscores_stripped(self):
        assert _sanitize_filename("___name___") == "name"

    def test_dots_replaced(self):
        assert _sanitize_filename("file.name.txt") == "file_name_txt"

    def test_hyphens_preserved(self):
        assert _sanitize_filename("my-file-name") == "my-file-name"

    def test_mixed_special_chars(self):
        result = _sanitize_filename("  Case (1) / Rev.2  ")
        # spaces and parens and slash become underscores, collapsed and stripped
        assert "__" not in result
        assert not result.startswith("_")
        assert not result.endswith("_")

    def test_empty_string(self):
        assert _sanitize_filename("") == ""

    def test_all_special_chars(self):
        result = _sanitize_filename("@#$%^&*()")
        assert result == ""
