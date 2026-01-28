import json
import os
import re
from pathlib import Path
import argparse
import logging

def validate_wb_config(wb_data):
    if not isinstance(wb_data, dict):
        raise ValueError("WB config must be a dict")
    if 'device' not in wb_data or not isinstance(wb_data['device'], dict):
        raise ValueError("WB config must have 'device' dict")
    device = wb_data['device']
    if 'id' not in device or 'channels' not in device:
        raise ValueError("Device must have 'id' and 'channels'")
    if not isinstance(device['channels'], list):
        raise ValueError("'channels' must be a list")

def convert_full_template(wb_device, translations, device_id_pattern, title):
    services = []
    catalog_id = 0
    all_channels = wb_device.get('channels', [])
    for subdevice in wb_device.get('subdevices', []):
        all_channels.extend(subdevice.get('device', {}).get('channels', []))
    
    for channel in all_channels:
        if channel.get('enabled') == False:
            continue
        english_name = channel['name']
        russian_name = translations.get(english_name, english_name)
        reg_type = channel.get('reg_type')
        ch_type = channel.get('type', 'value')
        readonly = channel.get('readonly', False)
        is_writable = not (reg_type == 'input' or readonly)
        units = channel.get('units', '').lower()
        # Special case for Error Code - always C_Integer
        if english_name.lower() == 'error code':
            service = {
                "name": russian_name,
                "type": "C_Option",
                "characteristics": [
                    {
                        "type": "C_Integer",
                        "link": [
                            {
                                "type": "Double",
                                "topicGet": "/devices/(1)/controls/" + english_name
                            }
                        ]
                    }
                ]
            }
        elif ch_type == 'switch':
            if reg_type in ['coil', 'holding']:
                service = {
                    "name": russian_name,
                    "type": "Switch",
                    "characteristics": [
                        {
                            "type": "On",
                            "link": [
                                {
                                    "type": "Integer",
                                    "topicGet": "/devices/(1)/controls/" + english_name,
                                    "topicSet": "/devices/(1)/controls/" + english_name + "/on"
                                }
                            ]
                        }
                    ]
                }
            else:
                continue
        elif ch_type == 'rel_humidity':
            if is_writable:
                # Writable humidity - C_Option
                link_type = 'C_Integer' if channel.get('scale', 1) == 0 else 'C_Double'
                display_name = russian_name + f" ({units})" if units else russian_name
                service = {
                    "name": display_name,
                    "type": "C_Option",
                    "characteristics": [
                        {
                            "type": link_type,
                            "link": [
                                {
                                    "type": "Double",
                                    "topicGet": "/devices/(1)/controls/" + english_name,
                                    "topicSet": "/devices/(1)/controls/" + english_name + "/on"
                                }
                            ]
                        }
                    ]
                }
                if link_type == 'C_Integer':
                    print(f"Note: Channel '{english_name}' uses C_Integer due to scale=0")
            else:
                # Read-only humidity - HumiditySensor
                service = {
                    "name": russian_name,
                    "type": "HumiditySensor",
                    "characteristics": [
                        {
                            "type": "CurrentRelativeHumidity",
                            "link": [
                                {
                                    "type": "Double",
                                    "topicGet": "/devices/(1)/controls/" + english_name
                                }
                            ]
                        }
                    ]
                }
        elif ch_type == 'lux':
            units = channel.get('units', 'lx').lower()
            display_name = russian_name + f" ({units})" if units else russian_name
            service = {
                "name": display_name,
                "type": "C_Option",
                "characteristics": [
                    {
                        "type": "C_Double",
                        "link": [
                            {
                                "type": "Double",
                                "topicGet": "/devices/(1)/controls/" + english_name
                            }
                        ]
                    }
                ]
            }
        elif ch_type == 'sound_level':
            units = channel.get('units', 'dBA')
            display_name = russian_name + f" ({units})" if units else russian_name
            service = {
                "name": display_name,
                "type": "C_Option",
                "characteristics": [
                    {
                        "type": "C_Double",
                        "link": [
                            {
                                "type": "Double",
                                "topicGet": "/devices/(1)/controls/" + english_name
                            }
                        ]
                    }
                ]
            }
        elif ch_type == 'temperature':
            if is_writable:
                # Writable temperature - C_Option
                link_type = 'C_Integer' if channel.get('scale', 1) == 0 else 'C_Double'
                display_name = russian_name + f" ({units})" if units else russian_name
                service = {
                    "name": display_name,
                    "type": "C_Option",
                    "characteristics": [
                        {
                            "type": link_type,
                            "link": [
                                {
                                    "type": "Double",
                                    "topicGet": "/devices/(1)/controls/" + english_name,
                                    "topicSet": "/devices/(1)/controls/" + english_name + "/on"
                                }
                            ]
                        }
                    ]
                }
                if link_type == 'C_Integer':
                    print(f"Note: Channel '{english_name}' uses C_Integer due to scale=0")
            else:
                # Read-only temperature - TemperatureSensor
                service = {
                    "name": russian_name,
                    "type": "TemperatureSensor",
                    "characteristics": [
                        {
                            "type": "CurrentTemperature",
                            "link": [
                                {
                                    "type": "Double",
                                    "topicGet": "/devices/(1)/controls/" + english_name,
                                    "minStep": 0.5,
                                    "checkValue": True
                                }
                            ]
                        }
                    ]
                }
        elif ch_type == 'concentration':
            if is_writable:
                # Writable concentration - C_Option
                link_type = 'C_Integer' if channel.get('scale', 1) == 0 else 'C_Double'
                display_name = russian_name + f" ({units})" if units else russian_name
                service = {
                    "name": display_name,
                    "type": "C_Option",
                    "characteristics": [
                        {
                            "type": link_type,
                            "link": [
                                {
                                    "type": "Double",
                                    "topicGet": "/devices/(1)/controls/" + english_name,
                                    "topicSet": "/devices/(1)/controls/" + english_name + "/on"
                                }
                            ]
                        }
                    ]
                }
                if link_type == 'C_Integer':
                    print(f"Note: Channel '{english_name}' uses C_Integer due to scale=0")
            else:
                # Read-only concentration - AirQualitySensor
                service = {
                    "name": russian_name,
                    "type": "AirQualitySensor",
                    "characteristics": [
                        {
                            "type": "VOCDensity",
                            "link": [
                                {
                                    "type": "Double",
                                    "topicGet": "/devices/(1)/controls/" + english_name
                                }
                            ]
                        }
                    ]
                }
        elif ch_type == 'value':
            if 'counter' in english_name.lower():
                service = {
                    "name": russian_name,
                    "visible": False,
                    "type": "C_PulseMeter",
                    "characteristics": [
                        {
                            "type": "C_PulseCount",
                            "link": [
                                {
                                    "type": "Double",
                                    "topicGet": "/devices/(1)/controls/" + english_name
                                }
                            ]
                        }
                    ]
                }
            elif reg_type == 'input' or readonly:
                if 'voltage' in english_name.lower() or 'volt' in english_name.lower() or 'v' in units:
                    service = {
                        "name": russian_name,
                        "type": "C_VoltMeter",
                        "characteristics": [
                            {
                                "type": "C_Volt",
                                "link": [
                                    {
                                        "type": "Double",
                                        "topicGet": "/devices/(1)/controls/" + english_name
                                    }
                                ]
                            }
                        ]
                    }
                elif 'current' in english_name.lower() or 'ampere' in english_name.lower():
                    service = {
                        "name": russian_name,
                        "type": "C_AmpereMeter",
                        "characteristics": [
                            {
                                "type": "C_Ampere",
                                "link": [
                                    {
                                        "type": "Double",
                                        "topicGet": "/devices/(1)/controls/" + english_name
                                    }
                                ]
                            }
                        ]
                    }
                elif 'distance' in english_name.lower():
                    service = {
                        "name": russian_name,
                        "type": "C_DistanceSensor",
                        "characteristics": [
                            {
                                "type": "C_Distance",
                                "link": [
                                    {
                                        "type": "Double",
                                        "topicGet": "/devices/(1)/controls/" + english_name
                                    }
                                ]
                            }
                        ]
                    }
                elif units.lower() in ['deg c', 'celsius']:
                    if is_writable:
                        # Writable temperature - C_Option
                        link_type = 'C_Integer' if channel.get('scale', 1) == 0 else 'C_Double'
                        display_name = russian_name + f" ({units})" if units else russian_name
                        service = {
                            "name": display_name,
                            "type": "C_Option",
                            "characteristics": [
                                {
                                    "type": link_type,
                                    "link": [
                                        {
                                            "type": "Double",
                                            "topicGet": "/devices/(1)/controls/" + english_name,
                                            "topicSet": "/devices/(1)/controls/" + english_name + "/on"
                                        }
                                    ]
                                }
                            ]
                        }
                        if link_type == 'C_Integer':
                            print(f"Note: Channel '{english_name}' uses C_Integer due to scale=0")
                    else:
                        # Read-only temperature - TemperatureSensor
                        service = {
                            "name": russian_name,
                            "type": "TemperatureSensor",
                            "characteristics": [
                                {
                                    "type": "CurrentTemperature",
                                    "link": [
                                        {
                                            "type": "Double",
                                            "topicGet": "/devices/(1)/controls/" + english_name,
                                            "minStep": 0.5,
                                            "checkValue": True
                                        }
                                    ]
                                }
                            ]
                        }
                elif units.lower() in ['v', 'voltage']:
                    service = {
                        "name": russian_name,
                        "type": "C_VoltMeter",
                        "characteristics": [
                            {
                                "type": "C_Volt",
                                "link": [
                                    {
                                        "type": "Double",
                                        "topicGet": "/devices/(1)/controls/" + english_name
                                    }
                                ]
                            }
                        ]
                    }
                elif units.lower() in ['a', 'current']:
                    service = {
                        "name": russian_name,
                        "type": "C_AmpereMeter",
                        "characteristics": [
                            {
                                "type": "C_Ampere",
                                "link": [
                                    {
                                        "type": "Double",
                                        "topicGet": "/devices/(1)/controls/" + english_name
                                    }
                                ]
                            }
                        ]
                    }
                elif units.lower() in ['w', 'power']:
                    # Power - C_Option with C_Double/C_Integer based on scale
                    link_type = 'C_Integer' if channel.get('scale', 1) == 0 else 'C_Double'
                    display_name = russian_name + f" ({units})" if units else russian_name
                    service = {
                        "name": display_name,
                        "type": "C_Option",
                        "characteristics": [
                            {
                                "type": link_type,
                                "link": [
                                    {
                                        "type": "Double",
                                        "topicGet": "/devices/(1)/controls/" + english_name
                                    }
                                ]
                            }
                        ]
                    }
                    if link_type == 'C_Integer':
                        print(f"Note: Channel '{english_name}' uses C_Integer due to scale=0")
                elif units.lower() in ['kwh', 'power_consumption']:
                    # Energy - C_Option with C_Double/C_Integer based on scale
                    link_type = 'C_Integer' if channel.get('scale', 1) == 0 else 'C_Double'
                    display_name = russian_name + f" ({units})" if units else russian_name
                    service = {
                        "name": display_name,
                        "type": "C_Option",
                        "characteristics": [
                            {
                                "type": link_type,
                                "link": [
                                    {
                                        "type": "Double",
                                        "topicGet": "/devices/(1)/controls/" + english_name
                                    }
                                ]
                            }
                        ]
                    }
                    if link_type == 'C_Integer':
                        print(f"Note: Channel '{english_name}' uses C_Integer due to scale=0")
                elif units.lower() in ['bar', 'mbar', 'pressure']:
                    # Pressure - C_Option with C_Double/C_Integer based on scale
                    link_type = 'C_Integer' if channel.get('scale', 1) == 0 else 'C_Double'
                    display_name = russian_name + f" ({units})" if units else russian_name
                    service = {
                        "name": display_name,
                        "type": "C_Option",
                        "characteristics": [
                            {
                                "type": link_type,
                                "link": [
                                    {
                                        "type": "Double",
                                        "topicGet": "/devices/(1)/controls/" + english_name
                                    }
                                ]
                            }
                        ]
                    }
                    if link_type == 'C_Integer':
                        print(f"Note: Channel '{english_name}' uses C_Integer due to scale=0")
                elif units.lower() in ['%, rh', 'rel_humidity']:
                    # Humidity - HumiditySensor
                    service = {
                        "name": russian_name,
                        "type": "HumiditySensor",
                        "characteristics": [
                            {
                                "type": "CurrentRelativeHumidity",
                                "link": [
                                    {
                                        "type": "Double",
                                        "topicGet": "/devices/(1)/controls/" + english_name
                                    }
                                ]
                            }
                        ]
                    }
                elif units.lower() in ['ppm', 'ppb', 'concentration']:
                    # Gas concentration - AirQualitySensor for VOC
                    service = {
                        "name": russian_name,
                        "type": "AirQualitySensor",
                        "characteristics": [
                            {
                                "type": "VOCDensity",
                                "link": [
                                    {
                                        "type": "Double",
                                        "topicGet": "/devices/(1)/controls/" + english_name
                                    }
                                ]
                            }
                        ]
                    }
                elif units.lower() in ['lx', 'illuminance']:
                    # Illuminance - C_Option with C_Double/C_Integer based on scale
                    link_type = 'C_Integer' if channel.get('scale', 1) == 0 else 'C_Double'
                    display_name = russian_name + f" ({units})" if units else russian_name
                    service = {
                        "name": display_name,
                        "type": "C_Option",
                        "characteristics": [
                            {
                                "type": link_type,
                                "link": [
                                    {
                                        "type": "Double",
                                        "topicGet": "/devices/(1)/controls/" + english_name
                                    }
                                ]
                            }
                        ]
                    }
                    if link_type == 'C_Integer':
                        print(f"Note: Channel '{english_name}' uses C_Integer due to scale=0")
                elif units.lower() in ['db', 'sound_level']:
                    # Sound level - C_Option with C_Double/C_Integer based on scale
                    link_type = 'C_Integer' if channel.get('scale', 1) == 0 else 'C_Double'
                    display_name = russian_name + f" ({units})" if units else russian_name
                    service = {
                        "name": display_name,
                        "type": "C_Option",
                        "characteristics": [
                            {
                                "type": link_type,
                                "link": [
                                    {
                                        "type": "Double",
                                        "topicGet": "/devices/(1)/controls/" + english_name
                                    }
                                ]
                            }
                        ]
                    }
                    if link_type == 'C_Integer':
                        print(f"Note: Channel '{english_name}' uses C_Integer due to scale=0")
                else:
                    link_type = 'C_Integer' if channel.get('scale', 1) == 0 else 'C_Double'
                    display_name = russian_name + f" ({units})" if units else russian_name
                    service = {
                        "name": display_name,
                        "type": "C_Option",
                        "characteristics": [
                            {
                                "type": link_type,
                                "link": [
                                    {
                                        "type": "Double",
                                        "topicGet": "/devices/(1)/controls/" + english_name
                                    }
                                ]
                            }
                        ]
                    }
                    if link_type == 'C_Integer':
                        print(f"Note: Channel '{english_name}' uses C_Integer due to scale=0")
            else:
                continue  # Skip writable value channels like setpoints
        else:
            # Default to C_Option with C_Double/C_Integer for unknown types
            link_type = 'C_Integer' if channel.get('scale', 1) == 0 else 'C_Double'
            display_name = russian_name + f" ({units})" if units else russian_name
            service = {
                "name": display_name,
                "type": "C_Option",
                "characteristics": [
                    {
                        "type": link_type,
                        "link": [
                            {
                                "type": "Double",
                                "topicGet": "/devices/(1)/controls/" + english_name
                            }
                        ]
                    }
                ]
            }
            if link_type == 'C_Integer':
                print(f"Note: Channel '{english_name}' uses C_Integer due to scale=0")
        
        if not any(s.get('name') == service['name'] for s in services):
            services.append(service)
    
    model_id = f"/devices/({device_id_pattern})/controls/.*/meta"
    return title, model_id, catalog_id, services

def convert_wb_to_spruthub(wb_path, spruthub_dir):
    with open(wb_path, 'r', encoding='utf-8') as f:
        wb_data = json.load(f)
    
    validate_wb_config(wb_data)
    
    wb_device = wb_data['device']
    device_type = wb_data['device_type']
    title = wb_device['name']
    if not title or title == 'WB-M1W2_template_title':
        title = wb_data.get('title', device_type)
    
    model = device_type
    device_id_pattern = wb_device['id'] + r'_[0-9]{1,3}'
    
    translations = wb_device.get('translations', {}).get('ru', {})
    
    title, model_id, catalog_id, services = convert_full_template(wb_device, translations, device_id_pattern, title)
    
    spruthub_data = {
        "name": title,
        "manufacturer": "Wiren Board",
        "model": model,
        "modelId": model_id,
        "catalogId": catalog_id,
        "services": services
    }
    
    output_file = Path(spruthub_dir) / f"{title.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '-').replace('.', '_')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(spruthub_data, f, ensure_ascii=False, indent=4)
    
    print(f"Converted {wb_path} to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Конвертер шаблонов WB в Spruthub. Обрабатывает файл или папку с JSON WB конфигами.")
    parser.add_argument('--input', required=True, help='Путь к файлу JSON или папке с файлами WB')
    parser.add_argument('--output', default='generated-templates', help='Папка для выходных файлов (создастся если не существует)')
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input path '{input_path}' does not exist.")
        return
    
    spruthub_dir = Path(args.output)
    spruthub_dir.mkdir(exist_ok=True)
    
    if input_path.is_file():
        files = [input_path]
    elif input_path.is_dir():
        files = list(input_path.glob('*.json'))
    else:
        print(f"Error: '{input_path}' is not a file or directory.")
        return
    
    total_files = len(files)
    success_count = 0
    error_count = 0
    
    print(f"Starting conversion of {total_files} files...")
    
    for wb_path in files:
        try:
            convert_wb_to_spruthub(wb_path, spruthub_dir)
            success_count += 1
            print(f"Successfully converted: {wb_path.name}")
        except Exception as e:
            error_count += 1
            print(f"Error converting {wb_path}: {e}")
    
    print(f"\nConversion completed: {success_count} successful, {error_count} errors.")

if __name__ == '__main__':
    main()