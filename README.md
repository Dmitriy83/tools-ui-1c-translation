# tools-ui-1c-translation

Pipeline для английского перевода расширения конфигурации **«Универсальные инструменты»** ([tools_ui_1c](https://github.com/tools-ui-1c/tools_ui_1c)) с использованием EDT LanguageTool («зависимый проект перевода») плюс набор скриптов, закрывающих пробелы автогенерации.

> Подробная техническая документация по форматам файлов, правилам перевода, EDT quirks и pipeline — в [CLAUDE.md](CLAUDE.md).
> Глубокое описание post-build шага — в [POSTBUILD_PATCHER.md](POSTBUILD_PATCHER.md).

## О проекте

«Универсальные инструменты» (`УИ_`) — расширение конфигурации с набором инструментов разработчика и администратора 1С: консоли запросов/кода/HTTP-запросов, навигатор по метаданным, редактор алгоритмов, групповая обработка справочников и документов и пр. Расширение исторически развивается на русском, английская версия отсутствует.

Этот репозиторий — словарь зависимого перевода + инфраструктура, которая позволяет:

- автоматически переводить изменения RU → EN через EDT LanguageTool,
- править остаточные ошибки автогенерации (post-build patcher),
- проверять, что в переведённом проекте не осталось кириллицы (`check_translated`),
- наполнять словари токенов и переводить файлы пакетно (`apply_*` + `translations_*`).

## Структура

```
tools-ui-1c-translation/
├── dictionaries_en/                  # зависимый проект перевода EDT
│   ├── DT-INF/DEPENDENT.PMF          # Parent-Project: Инструменты
│   ├── .project                      # dependentProjectNature
│   └── src/
│       ├── common_en.dict            # пословный shared-словарь
│       ├── common-camelcase_en.dict  # CamelCase-составные идентификаторы
│       └── Languages/English/        # объект целевого языка
├── scripts/                          # pipeline и диагностические скрипты
│   ├── pipeline/                     #   запускаются на каждой пересборке
│   ├── analysis/                     #   диагностика / одноразовый анализ
│   └── migration/                    #   гигиена словарей + применение TR-таблиц
├── CLAUDE.md                         # техническая документация (форматы, правила, quirks)
└── POSTBUILD_PATCHER.md              # описание post-build шага
```

## Как это работает

EDT не справляется с переводом 100% символов из-за особенностей токенизатора и неполноты внутренних словарей. Pipeline закрывает разрыв в три захода:

1. **EDT LanguageTool** делает базовый перевод используя `dictionaries_en/`.
2. **postbuild_patch** правит фиксированный набор остаточных багов перевода (неверные алиасы платформенных функций, поля платформенных объектов с обратным порядком слов, изредка — литералы в тестовых данных).
3. **check_translated** валидирует, что в коде переведённого проекта не осталось кириллицы.

Результат — английский исходник в `Инструменты_translated_project/` (под EDT) и далее экспортируемый в XML для возможного PR в основную репу.

## Pipeline (типовой проход после изменения словарей)

```
1. translate_configuration                # EDT LanguageTool: словарь -> EN артефакты
2. cleanup_orphan_modules.py              # удаление папок без .mdo
3. check_module_header_drift.py           # дрейф year/version в module-header
4. postbuild_patch.py                     # фиксы: StrStartWith, StatusCode, ...
5. clean translated_project (EDT)         # EDT перечитывает после postbuild
6. check_translated.py                    # ищет остаточную кириллицу (CODE+DOC)
```

Pipeline идемпотентный: повторный прогон даёт то же состояние.

Шаги 1, 5 — действия в EDT (через [EDT-MCP сервер](https://github.com/DitriXNew/EDT-MCP) с тулами `translate_configuration` / `export_configuration_to_xml` / `cleanup_orphan_modules`). Шаги 2–4, 6 — Python-скрипты этого репозитория.

## Требования

- **EDT 2026.1+** — основная целевая версия для автоматизации (на 2025.x словарь работает, но MCP-тулы не поддерживаются).
- **LanguageTool** — устанавливается отдельно через **Help → Install New Software**.
- **Java 17** (поставляется с EDT — Azul Zulu 17).
- **Python 3.10+** для pipeline-скриптов.
- **Git** для работы с upstream `tools_ui_1c`.

Опционально: [EDT-MCP плагин](https://github.com/DitriXNew/EDT-MCP) с тулами `translate_configuration` / `export_configuration_to_xml` / `generate_translation_strings` / `cleanup_orphan_modules` — для запуска pipeline через AI-ассистент.

## Быстрый старт

1. **Импортировать в EDT**:
   - исходное расширение: `C:/git/tools_ui_1c/src/Инструменты` (имя проекта в EDT — `Инструменты`)
   - базовая конфигурация: `ТестоваяДляРазработкиУИ` (нужна как родитель для расширения)
   - зависимый проект перевода: `dictionaries_en` (этот репозиторий)
2. Имя проекта-родителя в [DEPENDENT.PMF](dictionaries_en/DT-INF/DEPENDENT.PMF) должно совпадать с именем импортированного источника. По умолчанию — `Инструменты`.
3. Настроить пути в скриптах под свою машину: отредактировать константы `PROJ` / пути в начале каждого `scripts/<group>/*.py` (по умолчанию указывают на `C:/Users/<user>/AppData/Local/1C/1cedtstart/projects/Tools UI 1C/...`).
4. Прогнать процесс по [CLAUDE.md → Применение к новому модулю/файлу](CLAUDE.md#применение-к-новому-модулюфайлу).

## Скрипты

Полный обзор и параметры — в [CLAUDE.md → Тулинг](CLAUDE.md). Краткий перечень:

**Pipeline (запускаются после каждой пересборки EDT):**
- `cleanup_orphan_modules.py` — удаление мусорных папок модулей после переименований словаря
- `check_module_header_drift.py` — детектор дрейфа литералов (год/версия) в module-header
- `postbuild_patch.py` — фиксы остаточных багов перевода
- `check_translated.py` — детектор остаточной кириллицы по всему переведённому проекту (CODE / DOC)

**Анализ:**
- `extract_untranslated.py <файл>` — таблицы glossary + untranslated по одному файлу
- `extract_all_untranslated.py` — рекурсивно по всему `dictionaries_en/src/`
- `camelcase_tokens.py` — уникальные кириллические токены из camelcase-словаря
- `find_missing_dict_keys.py` — Cyrillic-идентификаторы из RU-исходника, которых нет в `common-camelcase_en.dict`
- `find_str_ids.py` — список `Стр*`-идентификаторов в RU-исходнике (аудит платформенных встроенных)

**Миграция / гигиена словарей:**
- `apply_translations.py <target> <translations.py>` — точечное применение TR-таблицы к одному файлу
- `apply_camelcase.py` — токенный перевод `common-camelcase_en.dict` через `camelcase_token_tr.py`
- `apply_small.py` — пакетная обработка нескольких файлов через `translations_small.py`
- `sort_dict.py` — алфавитная сортировка
- `proper_split.py` — переносить однословные идентификаторы в `common_en.dict`
- `fix_regions.py` — каноничные английские имена SSL-областей
- `fix_case.py` — нормализация PascalCase=lowercase легаси-записей
- `fix_camelcase.py` — case-нормализация + добавление недостающих идентификаторов
- `fix_str_builtins.py` — оверрайд `СтрНачинаетсяС=StrStartWith`
- `fix_platform_fields.py` — оверрайды платформенных полей (`КодСостояния=StatusCode` и т.д.)

## Связанные проекты

- [tools-ui-1c/tools_ui_1c](https://github.com/tools-ui-1c/tools_ui_1c) — исходник расширения (RU)
- [DitriXNew/EDT-MCP](https://github.com/DitriXNew/EDT-MCP) — MCP-сервер для EDT
- [Dmitriy83/EDT-MCP](https://github.com/Dmitriy83/EDT-MCP) — fork с тулами LanguageTool / Workspace export-import (PR'ы открыты в upstream)
- [vbondarevsky/Connector → httpconnector-translations](https://github.com/Dmitriy83/httpconnector-translations) — предшественник этого pipeline для библиотеки HTTPConnector

## Лицензия

Соответствует лицензии [tools_ui_1c](https://github.com/tools-ui-1c/tools_ui_1c).
