# tools-ui-1c-translation

Зависимый проект перевода EDT для расширения «Универсальные инструменты» (`УИ_`) с русского на английский.

## Контекст проекта

**Источник:** `C:/git/tools_ui_1c/src/Инструменты` — расширение конфигурации (CFE, тип `Adopted`/`AddOn`) на базе `ТестоваяДляРазработкиУИ`. EDT-проект называется `Инструменты`. Префикс объектов — `УИ_`. Vendor: ООО «Центр прикладных разработок».

**Состав для перевода:**
- 40 общих модулей (CommonModules)
- 42 обработки (DataProcessors)
- 2 отчёта (Reports)
- Справочники, общие команды, общие формы, общие шаблоны, HTTP-сервисы, роли, подсистемы

## Конфигурация EDT translation storages

**ВАЖНО:** в EDT-настройках проекта `Инструменты` оставлены **ТОЛЬКО контекстные словари** (per-module `.lstr` / `.trans` файлы под `dictionaries_en/src/<Category>/<Module>/`).

- Общий словарь `common-camelcase_en.dict` **УДАЛЁН** и **НЕ используется** EDT при переводе.
- `common_en.dict` остался, но в нём только display strings/литералы (Авто, Включая, …). Идентификаторы переводятся только через per-module `.Name=` записи.

**Следствие:** все переводы идентификаторов BSL должны быть в `Module_en.trans` каждого модуля как explicit `.Name=` записи. Глобальный токен-словарь не подхватится.

## Текущее состояние перевода

Полный аудит: `python scripts/analysis/audit_status.py`. На момент последнего снапшота:

| Категория | Файлов | .Name (cyr-valued) | .Word (cyr) | prose (cyr) |
|---|---:|---:|---:|---:|
| CommonModules | 128 | 13 256 (0) | 3 650 (0) | 3 364 (1) |
| DataProcessors | 620 | 28 013 (0) | 4 372 (0) | 6 050 (**2 426**) |
| Reports | 26 | 1 332 (**1 332**) | 95 (76) | 526 (517) |
| Catalogs | 19 | 406 (**404**) | 90 (82) | 19 (16) |
| CommonForms | 151 | 1 551 (**1 550**) | 145 (131) | 115 (86) |
| CommonCommands | 6 | 4 (**4**) | 0 | 2 (2) |
| HTTPServices | 3 | 36 (**30**) | 18 (5) | 0 |

**Что сделано:**

- **Все 40 CommonModules**: prose переведена агентами; `.Name=` идентификаторы заполнены (без кириллицы)
- **5 пилотов CommonModules с Opus-ревизией `.Name`** (правильный compound order): `УИ_РедакторКодаСервер`, `УИ_РедакторКодаВызовСервера`, `УИ_ОбщегоНазначенияКлиентСервер`, `УИ_КоннекторHTTP`, `УИ_Paste1CAPI` (первая волна — изначально качественно), плюс `УИ_ОбщегоНазначения`, `УИ_РедакторКодаКлиент`, `УИ_СтроковыеФункцииКлиентСервер`, `УИ_АлгоритмыСервер`, `УИ_РаботаСФормами` (вторая волна — Opus retranslate)
- **DataProcessors**: 73% prose переведено агентами (часть осталась после rate-limit), `.Name=` заполнены **алгоритмически с позиционной ошибкой** (`NameTable` вместо `TableName`)
- common-camelcase_en.dict удалён
- common_en.dict наполнен FROM_SOURCE_LANGUAGE из EDT (display literals)
- В EDT уже выполнен `translate_configuration` → `Инструменты_Перевод` translated project существует с переведёнными BSL модулями

**TODO** (в порядке приоритета):

1. **Sonnet retranslate `.Name=` в 17 оставшихся CommonModules** (23 уже сделаны: 5 пилотов + 5 Opus + 13 Sonnet через 2 волны)
2. **Sonnet retranslate `.Name=` в 42 DataProcessors** — фикс позиционных compound ordering
3. **Дотранслировать prose в DP** (2426 строк остались после rate-limit'а)
4. **Перевести Reports/Catalogs/CommonForms/Commands/HTTPServices** — почти не тронуты, нужны и `.Name=` и prose
5. **Follow-up pass для `.String.<X>.Key=` без Word** в уже-обработанных модулях — ранние волны переводили только `.Name=` и `.String.Word.<X>.Key=`, а compound-style `.String.КаталогБазы.Key=` остались позиционными. Гайд обновлён (теперь scope включает обе формы), но старые модули нужно перепрогнать. Затронутые модули — все из waves 1-2 (5 + 8 = 13 модулей)
6. **Cross-module consistency review** — обнаружен дрейф между агентами (например `NotificationOnCompletion` vs `CompletionNotification` — оба валидны, но не согласованы по проекту). Один проход с фиксированным глоссарием
7. После всего — `translate_configuration` в EDT, `cleanup_orphan_modules.py`, `check_translated.py`

## Активный workflow: Opus retranslate per module

**Задача:** для каждого модуля перевести значения `.Name=`, `.String.Word.X.Key=`, `.Description=`, `.NStr.X.Lines=`, `.Comment.X.Description=` в файлах `Module_en.trans` и `Module_en.lstr`.

### Style guides (всегда читать перед работой)

- [`prompts/MODULE_STYLE_GUIDE.md`](prompts/MODULE_STYLE_GUIDE.md) — общие правила перевода значений в `.lstr`/`.trans` per-module файлах
- [`prompts/NAME_RETRANSLATE_GUIDE.md`](prompts/NAME_RETRANSLATE_GUIDE.md) — **критическое правило compound order**: русский родительный (`ИмяТаблицы` = «имя таблицы») в английском требует **обратного порядка слов** (`TableName`, не `NameTable`)

### Базовые правила

1. **Никогда не менять ключи** — модифицировать только значения (правую часть `=`)
2. **Сохранять заголовок** `#Translations for: model` / `interface` и пустую строку после него
3. **Сохранять плейсхолдеры** `%1`, `%2` (то же количество и порядок)
4. **Java-properties escapes в значениях**: `\n` для перевода строки, `\:` для двоеточия, `\\` для backslash, `\=` для `=`
5. **Источник истины — KEY**: для `.Name=` имя берётся из последнего сегмента ключа перед `.Name`. Текущее значение может быть позиционно-неправильным — игнорировать его, выводить из ключа.
6. **Compound genitive reversal**: `ИмяX` → `XName`, `ТипX` → `XType`, `КодX` → `XCode`, `ТекстX` → `XText`, `ДатаX` → `XDate`, `НомерX` → `XNumber`, `АдресX` → `XAddress`, `РазмерX` → `XSize`, `ИндексX` → `XIndex`. Подробности и редкие случаи — в [NAME_RETRANSLATE_GUIDE.md](prompts/NAME_RETRANSLATE_GUIDE.md).
7. **Verb + compound сохраняет порядок верба**: `ПолучитьИмяФайла` → `GetFileName` (не GetNameFile)
8. **SSL canonical regions**: `ПрограммныйИнтерфейс` → `Public`, `СлужебныйПрограммныйИнтерфейс` → `Internal`, `СлужебныеПроцедурыИФункции` → `Private`, `ОбработчикиСобытий` → `EventHandlers`
9. **Project namespace**: `УИ_` → `UI_`
10. **Платформенные исключения** (positional translation даёт неверный английский): `КодСостояния=StatusCode`, `ПереносСтрок=NewLines`, `СимволыОтступа=PaddingSymbols`, `АдресРесурса=ResourceAddress`, `ИспользоватьАутентификациюОС=UseOSAuthentication`, `СтрНачинаетсяС=StrStartWith`

### Workflow для одного модуля

1. **Получить worklist**: `python scripts/analysis/extract_untranslated.py <путь к module_en.trans или .lstr>` — выдаст `untranslated.txt` и `glossary.txt`. ИЛИ запустить аудит: `python scripts/analysis/audit_status.py`.
2. **Запустить агент** на модуле:
   - Subagent_type: `general-purpose`
   - **Model: `sonnet`** (по умолчанию — на этой задаче по качеству сравнимо с Opus, но в ~5× дешевле). Эксперимент на 5 модулях (УИ_АлгоритмыКлиент, УИ_БуферОбменаКлиент, УИ_ДлительныеОперацииКлиент, УИ_ПарсерXML, УИ_ОбщегоНазначенияПовтИсп) показал 0 residual suspicious patterns и тот же fix density (~66%). Sonnet корректно применяет compound order, ловит SSL-canonical regions, узнаёт 1C platform names (XMLReader/XMLWriter/TimeConsumingOperation), self-reports сомнительные решения.
   - **Fallback: `opus`** — для очень больших модулей (>1000 строк), модулей с тяжёлой доменной семантикой (СКД, динамические запросы) или если Sonnet-вывод не устраивает на ревью.
   - В промпте дать: путь к `prompts/NAME_RETRANSLATE_GUIDE.md`, путь к `Module_en.trans` модуля, ссылку на референс уже-переведённого модуля (например `dictionaries_en/src/CommonModules/УИ_ОбщегоНазначения/Module_en.trans` — pilot retranslate, качественный).
3. **Если файл большой (>800 строк)** — chunk на 2-3 части (по 400-700 строк), один агент на чанк, потом склеить
4. **Агент работает in-place** (Edit) или пишет в `_done.txt` для чанков
5. **Верификация**: после агента — `grep -E "=Name[A-Z]|=Type[A-Z]|=Code[A-Z]|=Text[A-Z]|=Date[A-Z]" <file>` — должно вернуть 0 (или только legitimate compounds типа `TypeDescription` ← `ОписаниеТипа`)
6. **Cyr-residual check**: `python scripts/analysis/audit_status.py` — `.Name (cyr)` для модуля должно быть 0

### После пакета модулей

1. `git commit` промежуточных изменений в репе перевода
2. В EDT GUI или через MCP: `mcp__edt-mcp__translate_configuration` на `Инструменты` для `["en"]`
3. В EDT: `python scripts/pipeline/cleanup_orphan_modules.py` (удалит orphan-папки от переименований модулей)
4. Спот-чек: открыть `Инструменты_Перевод/src/CommonModules/<новое-имя>/Module.bsl`, убедиться что идентификаторы читаются естественно
5. `python scripts/pipeline/check_translated.py --skip-ru-mirrors` — финальный сканер кириллицы по translated_project

## Структура зависимого проекта

```
dictionaries_en/
├─ DT-INF/DEPENDENT.PMF         # Parent-Project: Инструменты
├─ .project                     # EDT-дескриптор с dependentProjectNature
└─ src/
   ├─ Configuration/            # синонимы и описание корня конфигурации
   ├─ CommonModules/<Имя>/      # Module_en.trans + Module_en.lstr + <Имя>_en.lstr (синоним) + <Имя>_en.trans (Name)
   ├─ DataProcessors/<Имя>/...  # тот же паттерн + ObjectModule/CommandModule/Forms/Templates
   ├─ Reports/<Имя>/...
   ├─ Catalogs/<Имя>/...
   ├─ CommonForms/<Имя>/...
   ├─ CommonCommands/<Имя>/...
   ├─ HTTPServices/<Имя>/...
   ├─ Roles/<Имя>/...
   ├─ Subsystems/<Имя>/...
   ├─ Languages/English/        # объект целевого языка
   └─ common_en.dict            # display strings (Авто, Включая, etc.)
```

## Форматы файлов

Все используют синтаксис java-properties (`key=value`, `#comment`).

### `.lstr` — переводы интерфейса
Заголовок: `#Translations for: interface`. Покрывает: синонимы объектов, имена реквизитов/табличных частей, заголовки команд (кнопок), значения перечислений, локализуемые `NStr()` строки.

```properties
#Translations for: interface

Synonym=Universal tools
Method.КакИсключение.Var.ТекстИсключения.NStr.HTTP\ %1\ %2\n%3.Lines=HTTP %1 %2\n%3
```

### `.trans` — переводы объектной модели
Заголовок: `#Translations for: model`. Покрывает: описания методов/параметров/возврата для синтакс-помощника, **explicit `.Name=` для перевода идентификаторов BSL**, переводы инлайн-комментариев.

```properties
#Translations for: model

Method.ПолучитьЗначение.Description=Returns a value by key
Method.ПолучитьЗначение.Name=GetValue
Method.ПолучитьЗначение.Param.Ключ.Description=Key of the value to return
Method.ПолучитьЗначение.Param.Ключ.Name=Key
Method.ПолучитьЗначение.Return.Description=Stored value or undefined.
```

### `.dict` — общие словари (только common_en.dict сейчас)
Заголовок: `#Translations for: common`. Display strings.

## Правила экранирования

**В ключах:** пробел `\ `, двоеточие `\:`, равно `\=`.
**В значениях:** перенос строки `\n`, литеральное двоеточие `\:`, backslash `\\`.
**Плейсхолдеры** `%1`, `%2` — без экранирования, сохранять количество/порядок.

## Паттерны ключей

### `.lstr` (interface)

| Префикс ключа | Значение |
|---|---|
| `Synonym` | Имя объекта в интерфейсе |
| `Comment` | Комментарий объекта |
| `Attribute.<Имя>.Synonym` | Имя реквизита |
| `Attribute.<Имя>.Title` | Заголовок реквизита формы |
| `Command.<Имя>.Title` | Заголовок команды формы |
| `Item.<Имя>.Title` | Заголовок элемента формы |
| `Form.<Имя>.Synonym` | Имя формы |
| `EnumValue.<Имя>.Synonym` | Имя значения перечисления |
| `Method.<Имя>.NStr.<EscKey>.Lines` | Локализуемая строка из BSL |

### `.trans` (model / documentation)

| Префикс ключа | Значение |
|---|---|
| `Description` | Описание объекта (модуля) |
| `Method.<Имя>.Description` | Описание метода |
| `Method.<Имя>.Name` | **Имя метода в английском (PascalCase)** |
| `Method.<Имя>.Param.<P>.Description` | Описание параметра |
| `Method.<Имя>.Param.<P>.Name` | **Имя параметра в английском** |
| `Method.<Имя>.Var.<V>.Name` | Имя локальной переменной |
| `Method.<Имя>.Return.Description` | Описание возвращаемого значения |
| `Method.<Имя>.String.Word.<rusword>.Key` | Перевод одного слова в строковых литералах |
| `Method.<Имя>.Comment.<EscKey>.Description` | Перевод инлайн-комментария |
| `Region.<Path>.Name` | **Каноничное имя региона** (Public/Internal/Private/...) |

## DT-INF/DEPENDENT.PMF

```
Manifest-Version: 1.0
Parent-Project: Инструменты
```

`Parent-Project` совпадает с именем EDT-проекта источника.

## Скрипты

- [scripts/analysis/audit_status.py](scripts/analysis/audit_status.py) — текущий статус по всем категориям (.Name/.Word/prose, % cyr-valued)
- [scripts/analysis/extract_untranslated.py](scripts/analysis/extract_untranslated.py) — `<file>` → glossary.txt + untranslated.txt для одного файла
- [scripts/analysis/extract_all_untranslated.py](scripts/analysis/extract_all_untranslated.py) — рекурсивно по всему dictionaries_en/src/
- [scripts/pipeline/cleanup_orphan_modules.py](scripts/pipeline/cleanup_orphan_modules.py) — удалить orphan-папки в translated_project после переименований
- [scripts/pipeline/check_translated.py](scripts/pipeline/check_translated.py) — финальный сканер кириллицы (CODE/DOC) в translated_project
- [scripts/pipeline/postbuild_patch.py](scripts/pipeline/postbuild_patch.py) — фиксы остаточных багов EDT (StrStartWith, поля платформы)
- [scripts/migration/fix_*.py](scripts/migration/) — точечные фиксы dict-файлов (regions, str_builtins, platform_fields)

`apply_camelcase.py`, `apply_translations.py`, `apply_small.py`, `camelcase_token_tr.py`, `camelcase_tokens.py`, `find_missing_dict_keys.py`, `proper_split.py`, `sort_dict.py` — **legacy от old token-dict workflow, не используются в текущем подходе**.

## EDT LanguageTool quirks (накопленные)

### Каноничные имена SSL/БСП регионов

| Русский | Каноничный английский |
|---|---|
| `ПрограммныйИнтерфейс` | `Public` |
| `СлужебныйПрограммныйИнтерфейс` | `Internal` |
| `СлужебныеПроцедурыИФункции` | `Private` |
| `ОбработчикиСобытий` | `EventHandlers` |
| `ОбработчикиСобытийФормы` | `FormEventHandlers` |
| `ОбработчикиСобытийЭлементовШапкиФормы` | `FormHeaderItemsEventHandlers` |
| `ОбработчикиКомандФормы` | `FormCommandsEventHandlers` |

Если регион переводится не каноничным именем — EDT для каждого метода в нём выдаст «method should be placed in standard region Public/Internal/Private».

### EDT платформенный словарь содержит неверные английские алиасы для некоторых встроенных функций

| Русский | EDT мапит (неверно) | Реальное имя в платформе |
|---|---|---|
| `СтрНачинаетсяС` | `StrStartsWith` | `StrStartWith` (без "s" в "Start") |

В runtime неверная форма падает с *«Procedure or function with the specified name is not defined»*. NB: `СтрЗаканчиваетсяНа` → `StrEndsWith` ПРАВИЛЬНО (с "s") — паттерн несимметричный. Фикс через explicit override в per-module `.trans` или через `postbuild_patch.py`.

### Платформенные поля с неестественным позиционным переводом

| Русский (positional) | Реальное в платформе |
|---|---|
| `КодСостояния` (CodeStatus) | `StatusCode` |
| `ПереносСтрок` (BreakLines) | `NewLines` |
| `СимволыОтступа` (SymbolsIndent) | `PaddingSymbols` |
| `АдресРесурса` (AddressResource) | `ResourceAddress` |
| `ИспользоватьАутентификациюОС` (UseAuthenticationOS) | `UseOSAuthentication` |

При работе с этими идентификаторами в `.Name=` переводе использовать реальное платформенное имя.

### Translated project содержит и исходник, и перевод

`Инструменты_Перевод/src/` содержит И английские модули (вывод перевода), И копии русских модулей (зеркало источника). При обработке translated_project ограничивать scope путями БЕЗ кириллицы (см. фильтр `has_cyrillic_path` в `postbuild_patch.py` / `check_translated.py`).

### Camelcase-словарь ранее токенизировал содержимое строковых литералов

Эта проблема была актуальна для HTTPConnector, где использовался `common-camelcase_en.dict`. У нас этот словарь удалён, поэтому токенизация литералов EDT не выполняется. См. [POSTBUILD_PATCHER.md](POSTBUILD_PATCHER.md) — описание режимов когда patcher нужен (большая часть для нашего проекта неактуальна).

## Координация работы между несколькими агентами / разработчиками

Если работаешь параллельно с другим разработчиком/агентом:

1. **Каждый берёт непересекающийся набор модулей** (категория или конкретные модули). Зафиксировать в чате/issue/git branch name.
2. **Работа в feature branches** — `git checkout -b retranslate/<category-or-module>`
3. **Перед началом работы**: `git fetch && git pull origin master`
4. **Регулярные коммиты по модулям** — после каждого пере-переведённого модуля делать commit с понятным сообщением (`Opus retranslate: УИ_АлгоритмыКлиент Module_en.trans`).
5. **Push в свою ветку**: `git push origin <branch>`
6. **Merge** через PR в master, после ревью спот-чек на pilot-модуле.
7. **Не запускать `translate_configuration` в EDT** во время чужой работы — он перепишет `Инструменты_Перевод/`. Координировать.
