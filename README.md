# Telegram AI Assistant

Telegram-бот для краткого анализа TXT-документов и ответов на вопросы по их содержимому. Проект поддерживает полностью локальный `DEMO_MODE` и production-режим с OpenAI Responses API.

## Назначение и архитектура

- `src/orchestrator/` — выбор модели и оценка задач;
- `src/telegram_ai_assistant/` — конфигурация, Telegram-обработчики, TXT-анализ и OpenAI-клиент;
- `document_store.py` — in-memory хранение одного документа на пользователя;
- `question_service.py` — вопросы по ограниченному контексту документа;
- `budget.py`, `confirmation.py`, `cost_estimator.py` — защитные ограничения;
- `html_formatter.py` — безопасное Telegram HTML-форматирование.

Документы не сохраняются на диск и не логируются. Изоляция выполняется по Telegram `user_id`, а TTL удаляет старые документы.

## Режимы работы

### DEMO_MODE=true

- локальные ответы без OpenAI API;
- `OPENAI_API_KEY` не читается;
- TXT-анализ работает без сетевых вызовов.

### DEMO_MODE=false

- используется `TELEGRAM_BOT_TOKEN`;
- `OPENAI_API_KEY` читается только в production-режиме;
- запросы идут через Responses API;
- применяются политика моделей, лимит стоимости, дневной бюджет и подтверждение дорогих запросов.

## Настройка

```powershell
Copy-Item .env.example .env
```

Для demo оставьте `DEMO_MODE=true`. Для production установите `DEMO_MODE=false` и заполните `TELEGRAM_BOT_TOKEN` и `OPENAI_API_KEY`. `.env` нельзя публиковать.

## Команды Telegram

- `/start` — запустить ассистента;
- `/help` — показать справку;
- `/ask <вопрос>` — задать вопрос по TXT-документу;
- `/clear` — удалить текущий документ;
- `/status` — показать режим и бюджет.

Обычный текст также обрабатывается ассистентом.

## Анализ TXT

Поддерживаются только `.txt`. После загрузки бот отправляет краткое резюме, до пяти фактов, статус, размер документа, число символов и пять локально сгенерированных вопросов. Вопрос задаётся через `/ask ваш вопрос`.

Инструкции внутри документа являются только данными и не выполняются. Документы разных пользователей не смешиваются, а новая загрузка заменяет старую.

## Лимиты и бюджет

Настраиваются через `.env`: `MAX_MESSAGE_LENGTH`, `MAX_DOCUMENT_BYTES`, `MAX_DOCUMENT_CHARACTERS`, `MAX_QUESTION_LENGTH`, `MAX_ANSWER_LENGTH`, `DOCUMENT_TTL_SECONDS`, `MAX_INPUT_TOKENS`, `MAX_OUTPUT_TOKENS`, `MAX_REQUEST_COST_USD`, `DAILY_BUDGET_USD` и `REQUIRE_CONFIRMATION_ABOVE_USD`.

Тарифы вынесены в отдельную конфигурацию. Бюджет хранится в памяти одного процесса.

## Установка и запуск

```text
python -m pip install -e ".[dev]"
```

```powershell
python -m telegram_ai_assistant.main
```

## Тестирование

```powershell
python -m pytest -q
```

Тесты используют mock-клиенты и не должны обращаться к Telegram или OpenAI.

## Безопасность

Не добавляйте `.env`, токены или API-ключи в GitHub, код, тесты, README или логи. При утечке ключа немедленно отзовите его у провайдера. Перед production-запуском проверьте лимиты и дневной бюджет.
