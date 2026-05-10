# Translation style guide — per-module .lstr / .trans files

You are translating a 1C:Enterprise BSL configuration's per-module dictionary files. Each file is java-properties format (`key=value`, `#comment`). You modify **only values** — keys are immutable lookup paths.

## File types

- **`Module_en.trans`** — model/documentation (`Description`, identifier `Name` renames, `String.Word` tokens)
- **`Module_en.lstr`** — interface strings (NStr from BSL, synonyms)
- **`<ModuleName>_en.lstr`** — module synonym (display name)
- **`<ModuleName>_en.trans`** — module identifier rename (`Name=...`)

## Hard rules

1. **Never modify keys** — only the right side of `=`.
2. **Preserve the header** — first line is `#Translations for: model` or `#Translations for: interface`. Keep blank line after it.
3. **Preserve placeholders** — `%1`, `%2`, ... must remain (same count, same order when grammar allows).
4. **Java-properties escapes in values**: `\n` for newline, `\:` for literal colon, `\\` for backslash, `\=` for equals. Spaces and most other chars stay raw.
5. **UTF-8 encoding, preserve line endings**.
6. **If a value is already English** (only Latin/punctuation/digits, no Cyrillic), leave it unchanged. Do NOT re-translate or "improve" already-translated entries.
7. **Identifier-style values** stay PascalCase, no spaces (see Identifier rules below).

## Value translation by key suffix

### `.Description` → English prose
Method/parameter/return descriptions, doc-comment translations. Style: concise, technical, declarative. Match the style of standard 1C SSL English documentation.
- `Method.X.Description=Возвращает имя файла.` → `Method.X.Description=Returns the file name.`
- `Method.X.Param.Y.Description=ссылка на объект` → `Method.X.Param.Y.Description=reference to the object`

### `.Name` → English PascalCase identifier
Token-by-token transliteration of the Russian compound, using these anchor decisions (matching the project's token glossary):

**Verbs:** `Получить→Get`, `Установить→Set`, `Добавить→Add`, `Удалить→Delete`, `Найти→Find`, `Создать→Create`, `Записать→Write`, `Прочитать→Read`, `Сохранить→Save`, `Загрузить→Load`, `Открыть→Open`, `Закрыть→Close`, `Выполнить→Execute`, `Проверить→Check`, `Изменить→Change`, `Обновить→Update`, `Очистить→Clear`, `Заполнить→Fill`, `Начать→Start`, `Завершить→Finish`, `Выбрать→Select`, `Сравнить→Compare`, `Преобразовать→Convert`, `Отправить→Send`, `Зарегистрировать→Register`, `Подготовить→Prepare`, `Применить→Apply`, `Сбросить→Reset`, `Отменить→Cancel`, `Выгрузить→Unload/Upload (context-dependent)`

**Nouns:** `Имя→Name`, `Тип→Type`, `Значение→Value`, `Описание→Description`, `Объект→Object`, `Данные→Data`, `Текст→Text`, `Строка→String/Row` (String for type, Row for table-row), `Число→Number`, `Дата→Date`, `Время→Time`, `Файл→File`, `Поле→Field`, `Элемент→Item`, `Группа→Group`, `Список→List`, `Массив→Array`, `Структура→Structure`, `Соответствие→Map`, `Таблица→Table`, `Колонка→Column`, `Реквизит→Attribute`, `Команда→Command`, `Параметр→Parameter`, `Настройка→Setting`, `Форма→Form`, `Запрос→Query`, `Отчет→Report`, `Документ→Document`, `Справочник→Catalog`, `Регистр→Register`, `Подсистема→Subsystem`, `Роль→Role`, `Пользователь→User`, `Сообщение→Message`, `Ошибка→Error`, `Версия→Version`, `Размер→Size`, `Длина→Length`, `Цвет→Color`, `Идентификатор→Identifier`, `Состояние→State`, `Класс→Class`, `Модуль→Module`, `Метод→Method`, `Функция→Function`, `Процедура→Procedure`, `Свойство→Property`, `Менеджер→Manager`, `Сервис→Service`, `Хранилище→Storage`, `Кэш→Cache`, `Дерево→Tree`, `Узел→Node`, `Шаблон→Template`, `Адрес→Address`, `Источник→Source`, `Назначение→Destination`, `Результат→Result`, `Условие→Condition`, `Запись→Record`, `Сессия→Session`, `Соединение→Connection`, `Подключение→Connection`, `Поток→Stream`, `Контекст→Context`, `Область→Area`, `Раздел→Section`, `Категория→Category`, `Признак→Flag`, `Метка→Tag`, `Заголовок→Header`, `Страница→Page`, `Кнопка→Button`, `Окно→Window`, `Действие→Action`, `Событие→Event`, `Обработчик→Handler`, `Приложение→Application`, `Конфигурация→Configuration`, `Расширение→Extension`, `Сервер→Server`, `Клиент→Client`, `База→Database`, `Платформа→Platform`, `Метаданные→Metadata`, `Компоновка→DataComposition`, `Схема→Schema`, `Граница→Boundary`, `Ссылка→Reference`, `Путь→Path`, `Код→Code`, `Алгоритм→Algorithm`, `Редактор→Editor`, `Запрос→Query`

**Prepositions:** `По→By`, `В/в→In/in`, `Из/из→From/from`, `Для/для→For/for`, `На/на→On/on`, `К/к→To/to`, `С/с→With/with`, `Без/без→Without/without`, `После/после→After/after`, `До/до→Before/before`, `При/при→On/on` (event prefix), `И/и→And/and`, `Или/или→Or/or`, `Не/не→Not/not`

**Project prefix:** `УИ_→UI_`

**Single Cyrillic letters:** transliterate (А→A, Б→B, В→V, Г→G, Д→D, Е→E, Ж→Zh, З→Z, И→I, Й→J, К→K, Л→L, М→M, Н→N, О→O, П→P, Р→R, С→S, Т→T, У→U, Ф→F, Х→Kh, Ц→Ts, Ч→Ch, Ш→Sh, Щ→Sch, Ы→Y, Э→E, Ю→Ju, Я→Ja).

**1C platform property exceptions** (tokenizer reverses word order — use the actual platform name):
- `КодСостояния→StatusCode` (NOT CodeStatus)
- `ПереносСтрок→NewLines` (NOT BreakLines)
- `СимволыОтступа→PaddingSymbols`
- `АдресРесурса→ResourceAddress`
- `ИспользоватьАутентификациюОС→UseOSAuthentication`
- `СтрНачинаетсяС→StrStartWith` (NOT StrStartsWith)

Examples:
- `Method.ПолучитьИмяФайла.Name=GetFileName`
- `Method.ДобавитьЭлемент.Name=AddItem`
- `Method.X.Param.ИмяСвойства.Name=PropertyName`
- `Method.X.Var.ТекущаяСтрока.Name=CurrentRow` (or CurrentString — context)

### `.NStr.<escapedRussian>.Lines` → English NStr translation
The `<escapedRussian>` part of the KEY is the source NStr string (with java-properties escaping in the key portion). Translate the VALUE to natural English. Preserve `%1`, `%2`, `\n`. Adjust grammar for English.
- `Method.X.NStr.Файл\ %1\ не\ найден.Lines=Файл %1 не найден` → `=File %1 not found`
- `Method.X.NStr.Не\ удалось\ загрузить.Lines=Не удалось загрузить` → `=Failed to load`

### `.String.Word.<word>.Key` → English equivalent of the single word
Single-word value translation. Lowercase Russian word in key → lowercase English word in value (preserve case roughly).
- `Method.X.String.Word.файл.Key=файл` → `=file`
- `Method.X.String.Word.Имя.Key=Имя` → `=Name`

### `Region.<rusName>.Name` → canonical SSL English name
Use the canonical 1C SSL standard names:
- `Region.ПрограммныйИнтерфейс.Name=Public`
- `Region.СлужебныйПрограммныйИнтерфейс.Name=Internal`
- `Region.СлужебныеПроцедурыИФункции.Name=Private`
- `Region.ОбработчикиСобытий.Name=EventHandlers`
- `Region.ОбработчикиСобытийФормы.Name=FormEventHandlers`
- `Region.ОбработчикиКомандФормы.Name=FormCommandsEventHandlers`

For non-canonical region names (custom regions like `КонтейнерЗначенияДляХраненияНаФорме`), translate as PascalCase compound.

### `Synonym=<russian>` → English display name
The display name in the UI. **Spaces allowed** (this is a string, not an identifier). Sentence-case in most cases.
- `Synonym=Редактор кода сервер` → `Synonym=Code editor server`
- `Synonym=Общего назначения клиент сервер` → `Synonym=General purpose client server`

### `Comment.<key>.Description` → English comment text
Inline code-comment translations. Translate as English prose, preserving any embedded BSL syntax in the original.

## Output

Apply edits to the SAME file (overwrite). Use the Edit tool with full file content via Write if extensive, or per-line Edit if targeted.

Verify before completing:
1. No Cyrillic remaining in any value (run a grep mentally over your output).
2. Header line preserved.
3. Blank line after header preserved.
4. Same number of lines as input.
