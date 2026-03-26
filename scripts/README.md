# Конвертер шаблонов WB в Spruthub MQTT

Этот скрипт (`convert_templates.py`) конвертирует шаблоны устройств Modbus из формата WB (Wiren Board) в формат Spruthub MQTT.

## Описание

Скрипт читает конфигурационные файлы WB из указанной папки или файла и генерирует соответствующие шаблоны Spruthub в папку `generated-templates/`. Поддерживает только полный режим (full), где включаются все каналы устройства с корректными типами сервисов.

## Использование

```bash
python3 convert_templates.py --input <path> [--output <output_dir>]
```

- `<path>`: Путь к файлу JSON или папке с файлами WB (например, `wb-device-modbus-templates/` или `wb-device-modbus-templates/config-wb-ms-thls-v2.json`).
- `<output_dir>`: Папка для выходных файлов (по умолчанию `generated-templates`, создастся если не существует).

Если указана папка в input, обрабатываются все `*.json` файлы в ней.

## Опции

- `--input`: Обязательный. Путь к входному файлу или папке.
- `--output`: Опциональный. Папка для выходных файлов (по умолчанию `generated-templates`).

## Примеры

- Обработка всей папки с выводом в дефолтную папку:
  ```bash
  python3 convert_templates.py --input wb-device-modbus-templates/
  ```

- Обработка одного файла с кастомной выходной папкой:
  ```bash
  python3 convert_templates.py --input wb-device-modbus-templates/config-wb-ms-thls-v2.json --output my-templates
  ```

- Обработка папки с кастомным выводом:
  ```bash
  python3 convert_templates.py --input templates/ --output output/
  ```

## Особенности

- **Русские названия**: Имена сервисов берутся из секции translations.ru WB-конфига (если есть), иначе английские. Топики MQTT всегда английские для совместимости с устройствами WB.
- **Read-only логика**: Характеристики read-only, если `reg_type == 'input'` или `readonly == true` (только `topicGet`). Иначе writable (`topicGet` + `topicSet`).
- **Units в названиях**: Для C_Option служб добавляются units в скобках (например, "Illuminance (lx)"). Дефолты: lux -> 'lx', sound_level -> 'dBA'.
- **Типы характеристик**: TemperatureSensor, HumiditySensor, AirQualitySensor (VOC), C_VoltMeter, C_AmpereMeter, C_DistanceSensor, C_Option (generic числа), Switch, ContactSensor (только true contacts). Для setpoint температуры — C_Option writable.
- **Автоопределение типа**: C_Option использует C_Double по умолчанию, но если `scale=0` в WB конфиге, то C_Integer (выводится Note).
- **Обработка ошибок**: Пропускает поврежденные файлы с выводом ошибки.
- **Вывод**: Показывает прогресс, количество обработанных файлов, ошибки.
- **Имена файлов**: Очищены от символов `/`, `(`, `)`, `.` (заменены на `-`, `_`).

## Зависимости

- Python 3
- Стандартные библиотеки: json, os, re, pathlib, argparse

## Примечания

- Скрипт создает папку `generated-templates/` автоматически.
- Для числовых каналов без специального типа используется C_Option с C_Double/C_Integer.
- Если scale не указан, используется C_Double.
- Read-only характеристики не имеют `topicSet`.
- Units добавляются только для C_Option служб, если присутствуют в конфиге или дефолты.
- Translations из WB-конфига используются только для русских названий сервисов, но не копируются в выходные файлы.