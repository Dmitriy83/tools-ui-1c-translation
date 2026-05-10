# Re-translate .Name= identifiers in 1C per-module .trans files

You re-translate Russian-language **identifier names** in per-module `Module_en.trans` files. The current English values were produced by a positional token-substitution algorithm and contain many word-order errors. Your job is to fix them by deriving the correct English from the **key**.

## Source of truth: the KEY, not the current value

The KEY tells you what to translate. Examples:

```
Method.ПолучитьИмяФайла.Name=GetNameFile        ← bad value, ignore
                          ^^^^^^^^^^^^^^^^
              correct: GetFileName (Get + FileName, where FileName is "name of file" with English compound order)

Method.ПолучитьИмяФайла.Param.ИмяТаблицы.Name=NameTable   ← bad value, ignore
                                       ^^^^^^^^^^
                          correct: TableName (compound: "name of table")

Method.ПолучитьИмяФайла.Var.КодОшибки.Name=CodeError   ← bad value, ignore
                                    ^^^^^^^^^^^
                          correct: ErrorCode

Region.ПрограммныйИнтерфейс.Name=ProgramInterface    ← bad value
                            ^^^^^^^^^^^^^^^^
              correct: Public (canonical SSL standard region name)
```

The Russian identifier is the **last segment of the key before `.Name`**:
- `Method.ПолучитьИмяФайла.Name` → identifier is `ПолучитьИмяФайла`
- `Method.X.Param.ИмяТаблицы.Name` → identifier is `ИмяТаблицы`
- `Method.X.Var.КодОшибки.Name` → identifier is `КодОшибки`
- `Region.ПрограммныйИнтерфейс.Name` → identifier is `ПрограммныйИнтерфейс`

## CRITICAL RULE: Russian noun+genitive compounds become English with REVERSED word order

This is the #1 fix needed. Russian uses noun+genitive ("name OF table"); English uses adjective-style compound with the modifier first.

| Russian (token order: A B) | Bad positional (A+B) | **CORRECT (reversed: B+A)** |
|---|---|---|
| `ИмяФайла` (Name of File) | `NameFile` | **`FileName`** |
| `ИмяТаблицы` | `NameTable` | **`TableName`** |
| `ИмяКолонки` | `NameColumn` | **`ColumnName`** |
| `ИмяРеквизита` | `NameAttribute` | **`AttributeName`** |
| `ИмяМетода` | `NameMethod` | **`MethodName`** |
| `ИмяПараметра` | `NameParameter` | **`ParameterName`** |
| `ИмяОбъекта` | `NameObject` | **`ObjectName`** |
| `ИмяТипа` | `NameType` | **`TypeName`** |
| `ИмяПоля` | `NameField` | **`FieldName`** |
| `ИмяСвойства` | `NameProperty` | **`PropertyName`** |
| `ТипДанных` (Type of Data) | `TypeData` | **`DataType`** |
| `ТипЗначения` | `TypeValue` | **`ValueType`** |
| `ТипОбъекта` | `TypeObject` | **`ObjectType`** |
| `ТипПараметра` | `TypeParameter` | **`ParameterType`** |
| `ТипФайла` | `TypeFile` | **`FileType`** |
| `КодОшибки` (Code of Error) | `CodeError` | **`ErrorCode`** |
| `КодСостояния` | `CodeStatus` | **`StatusCode`** |
| `КодВозврата` | `CodeReturn` | **`ReturnCode`** |
| `ТекстОшибки` (Text of Error) | `TextError` | **`ErrorText`** |
| `ТекстСообщения` | `TextMessage` | **`MessageText`** |
| `ТекстЗапроса` | `TextQuery` | **`QueryText`** |
| `ДатаНачала` (Date of Start) | `DateStart` | **`StartDate`** |
| `ДатаОкончания` | `DateEnd` | **`EndDate`** |
| `ДатаСоздания` | `DateCreation` | **`CreationDate`** |
| `НомерСтроки` (Number of Line) | `NumberLine` | **`LineNumber`** |
| `НомерКолонки` | `NumberColumn` | **`ColumnNumber`** |
| `АдресЭлектроннойПочты` | `AddressEmail` | **`EmailAddress`** |
| `АдресСервера` | `AddressServer` | **`ServerAddress`** |
| `РазмерФайла` (Size of File) | `SizeFile` | **`FileSize`** |
| `ИндексСтроки` (Index of Row) | `IndexRow` | **`RowIndex`** |
| `СписокЗначений` (List of Values) | `ListValue` | **`ValueList`** |

**Rule of thumb:** if the Russian compound is `<NounA><NounA-genitive>`, English is `<NounB><NounA>` (reverse).

## Verb + compound (verbs keep position, but inner compound reverses)

| Russian | Correct English |
|---|---|
| `ПолучитьИмяФайла` (Get + name-of-file) | `GetFileName` (not `GetNameFile`) |
| `УстановитьТипДанных` | `SetDataType` |
| `СоздатьНовыйДокумент` (Create + new + document) | `CreateNewDocument` (preserves order — adjective+noun) |
| `НайтиПоИмени` (Find + by + name) | `FindByName` (verb + preposition + noun) |
| `ВыполнитьВБезопасномРежиме` (Execute + in + safe + mode) | `ExecuteInSafeMode` |
| `ЗначениеРеквизитаОбъекта` (Value + of-attribute + of-object) | `ObjectAttributeValue` (chained genitive — innermost is the topmost) |
| `ОписаниеТипаДанных` (Description + of-type + of-data) | `DataTypeDescription` |

## Other rules

- **Adjective + noun (Russian): preserve order**: `НовыйОбъект` (new object) → `NewObject`, `ТекущийПользователь` → `CurrentUser`. Adjectives include: `Новый/Новая`, `Текущий/Текущая`, `Старый`, `Главный`, `Основной`, `Полный`, `Активный`, `Внутренний`, `Внешний`, `Локальный`, `Системный`.
- **Verb + noun (action methods): preserve order**: `ПолучитьЗначение` → `GetValue`, `УстановитьИмя` → `SetName`, `ДобавитьЭлемент` → `AddItem`. Verb stems: `Получить→Get`, `Установить→Set`, `Добавить→Add`, `Удалить→Delete`, `Создать→Create`, `Найти→Find`, `Записать→Write`, `Прочитать→Read`, `Сохранить→Save`, `Загрузить→Load`, `Открыть→Open`, `Закрыть→Close`, `Выполнить→Execute`, `Проверить→Check`, `Изменить→Change`, `Обновить→Update`, `Очистить→Clear`, `Заполнить→Fill`, `Начать→Start`, `Завершить→Finish`, `Выбрать→Select`.
- **Prepositions stay in English position**: `ПоИмени`/`ByName`, `ВТранзакции`/`InTransaction`, `НаКлиенте`/`OnClient`, `ИзСтроки`/`FromString`, `ДляЭлемента`/`ForItem`, `КОбъекту`/`ToObject`, `СПараметрами`/`WithParameters`.
- **Project namespace**: `УИ_` → `UI_`. So `УИ_ОбщегоНазначения` → `UI_GeneralPurpose`, `УИ_АлгоритмыСервер` → `UI_AlgorithmsServer`.
- **Standard SSL regions** (canonical English):
  - `Region.ПрограммныйИнтерфейс.Name` → `Public`
  - `Region.СлужебныйПрограммныйИнтерфейс.Name` → `Internal`
  - `Region.СлужебныеПроцедурыИФункции.Name` → `Private`
  - `Region.ОбработчикиСобытий.Name` → `EventHandlers`
- **1C platform field exceptions** (don't follow positional, use these):
  - `КодСостояния` → `StatusCode`
  - `ПереносСтрок` → `NewLines`
  - `СимволыОтступа` → `PaddingSymbols`
  - `АдресРесурса` → `ResourceAddress`
  - `ИспользоватьАутентификациюОС` → `UseOSAuthentication`
  - `СтрНачинаетсяС` → `StrStartWith` (NOT `StrStartsWith`)
- **Single-letter Cyrillic identifiers** (rare, in test data): transliterate (`А→A`, `Б→B`, `В→V`, etc.)

## .String.Word.<rusword>.Key — single-word translation

The KEY contains a single Russian word; the VALUE is its English equivalent. These are NOT compounds — just one-word translations:
- `String.Word.файл.Key=file`
- `String.Word.Имя.Key=Name`
- `String.Word.код.Key=code`
- `String.Word.и.Key=and`

For these, just produce the natural English equivalent of the single Russian word, preserving rough case (lowercase Russian → lowercase English unless it's a proper noun or platform name).

## Method

1. Read the trans file.
2. For every `key=value` line where the key ends with `.Name` OR matches `.String.Word.<X>.Key`:
   - Extract the Russian identifier from the key
   - Determine correct English (apply rules above)
   - Replace the value (use Edit tool with old_string=current line, new_string=corrected line)
3. Leave all other lines unchanged.
4. Do NOT modify `.Description=`, `.NStr.X.Lines=`, `.Comment.X.Description=` lines (those are prose, already translated).

## Output

After processing, report:
- entries reviewed: <count>
- entries fixed (value changed): <count>
- examples of bad-→-fixed: 5-10 examples showing original wrong vs your correction
- any uncertain decisions (where you're not sure about correct English)

Be ruthless about fixing positional `XY` compounds — even if the existing value "looks like English", if it's `NameTable`-style positional, FIX IT to `TableName`.
