from telegram_ai_assistant.html_formatter import format_html, split_html


def test_format_html_escapes_dynamic_text_and_formats_blocks():
    formatted = format_html("КРАТКОЕ РЕЗЮМЕ:\n<b>bold</b> <i>italic</i> <code>code</code> & текст\n/ask вопрос")
    assert "📝 <b>РЕЗЮМЕ</b>" in formatted
    assert "<b>bold</b>" in formatted
    assert "<i>italic</i>" in formatted
    assert "<code>code</code>" in formatted
    assert "&amp; текст" in formatted
    assert "<code>/ask вопрос</code>" in formatted


def test_format_html_escapes_dangerous_html_tags():
    formatted = format_html("<script>alert('x')</script>")
    assert "&lt;script&gt;" in formatted
    assert "&lt;/script&gt;" in formatted
    assert "<script>" not in formatted


def test_split_html_respects_limit():
    chunks = split_html("абв " * 2000, limit=500)
    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)


def test_chat_elden_ring_markdown_becomes_safe_telegram_html():
    formatted = format_html("**Elden Ring** — <danger>\n\nНовый абзац.")
    assert "<b>Elden Ring</b>" in formatted
    assert "**" not in formatted
    assert "&lt;danger&gt;" in formatted
    assert "\n\n" in formatted


def test_format_html_supports_markdown_variants_and_preserves_safe_tags():
    formatted = format_html("**bold** *italic* `code`\n<b>already bold</b>\n- item")
    assert "<b>bold</b>" in formatted
    assert "<i>italic</i>" in formatted
    assert "<code>code</code>" in formatted
    assert "<b>already bold</b>" in formatted
    assert "• item" in formatted
    assert "**" not in formatted
    assert "*italic*" not in formatted
    assert "`code`" not in formatted
