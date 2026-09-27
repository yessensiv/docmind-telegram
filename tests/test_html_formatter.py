from telegram_ai_assistant.html_formatter import format_html, split_html


def test_format_html_escapes_dynamic_text_and_formats_blocks():
    formatted = format_html("КРАТКОЕ РЕЗЮМЕ:\n<b>опасный</b> & текст\n/ask вопрос")
    assert "<b>КРАТКОЕ РЕЗЮМЕ:</b>" in formatted
    assert "&lt;b&gt;опасный&lt;/b&gt;" in formatted
    assert "&amp; текст" in formatted
    assert "<code>/ask вопрос</code>" in formatted


def test_split_html_respects_limit():
    chunks = split_html("абв " * 2000, limit=500)
    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)
