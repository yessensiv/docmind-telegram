import pytest

from telegram_ai_assistant.document_limits import MAX_DOCUMENT_BYTES, MAX_DOCUMENT_CHARACTERS
from telegram_ai_assistant.document_service import DocumentError, analyze_txt


def test_small_txt_is_analyzed_in_memory():
    result = analyze_txt("notes.txt", "Title\nBody".encode())
    assert result.characters == 10
    assert result.lines == 2
    assert result.preview == ("Title", "Body")
    assert "Demo-резюме" in result.summary


@pytest.mark.parametrize("filename", ["report.pdf", "report.docx", "report.csv"])
def test_non_txt_is_rejected(filename):
    with pytest.raises(DocumentError, match="только TXT"):
        analyze_txt(filename, b"content")


def test_file_at_byte_limit_is_allowed_when_text_is_valid():
    content = b"a" * MAX_DOCUMENT_BYTES
    with pytest.raises(DocumentError, match="слишком длинный"):
        analyze_txt("large.txt", content)


def test_file_over_byte_limit_is_rejected():
    with pytest.raises(DocumentError, match="слишком большой"):
        analyze_txt("large.txt", b"a" * (MAX_DOCUMENT_BYTES + 1))


def test_text_at_character_limit_is_allowed_by_character_check():
    content = ("a" * (MAX_DOCUMENT_CHARACTERS - 1) + "\n").encode()
    result = analyze_txt("limit.txt", content)
    assert result.characters == MAX_DOCUMENT_CHARACTERS


def test_text_over_character_limit_is_rejected():
    content = ("a" * (MAX_DOCUMENT_CHARACTERS + 1)).encode()
    with pytest.raises(DocumentError, match="слишком длинный"):
        analyze_txt("long.txt", content)


def test_invalid_encoding_is_rejected():
    with pytest.raises(DocumentError, match="UTF-8"):
        analyze_txt("bad.txt", b"\xff\xfe")


def test_empty_document_is_rejected():
    with pytest.raises(DocumentError, match="пуст"):
        analyze_txt("empty.txt", b" \n\t")
