from telegram_ai_assistant.suggested_questions import generate_questions


def test_generates_five_local_questions_without_external_services():
    questions = generate_questions("Status: complete\nThe project is ready")
    assert 3 <= len(questions) <= 5
    assert all(question.endswith("?") for question in questions)
