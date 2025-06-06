import os
import json
import copy
import logging
logs = logging.getLogger(__name__)

class settings:
    def __init__(self, settings_path : str = "settings.json"):
        self.settings_path = settings_path
        self.settings_json_result = None
        self.settings_json_result_ = None

        self.settings_dict_example = {
            "backup_folders": [
                "~/Музыка",
                "~/Изображения"
            ],
            "backup_destination": "Backups",
            "schedule_seconds": 5
        }

    def _verify_folders(self):
        logs.debug("Начала работы функции _verify_folders.")
        
        backup_folders = self.settings_json_result["backup_folders"]
        backup_destination = self.settings_json_result["backup_destination"]

        current_backup_folders = []

        for path in backup_folders:
            abs_path = os.path.abspath(os.path.expanduser(path))
            if not os.path.exists(abs_path):
                logs.warning(f"Папка по пути {path} не доступна!")
                return False
            current_backup_folders.append(abs_path)
        
        self.settings_json_result["backup_folders"] = current_backup_folders
            
        if not os.path.exists(os.path.expanduser(backup_destination)):
            if "~" in backup_destination:
                backup_destination  = os.path.expanduser(backup_destination)
            logs.warning(f"Создал папку для бекапов по пути {backup_destination}")
            os.makedirs(backup_destination)            
            self.settings_json_result["backup_destination"] = os.path.abspath(os.path.expanduser(backup_destination))

        return True
    
    def _verify_settings(self):

        logs.debug("Начала работы функции _verify_settings.")

        try:
            logs.debug(f"Попытка открыть файл {self.settings_path}.")
            with open(self.settings_path, "r") as file:
                settings_json_result = json.load(file)
            logs.debug(f"Открыл файл {self.settings_path}. {settings_json_result}")
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            settings_json_result = {}
        
        self.settings_json_result_ = copy.deepcopy(settings_json_result)

        for key, value in self.settings_dict_example.items():
            if key not in settings_json_result:
                logs.warning(f"Настройки {key} не было в настройках!")
                settings_json_result[key] = value
            else:
                if isinstance(value, dict) and isinstance(self.settings_dict_example[key], dict):
                    settings_json_result[key] = value
                else:
                    if not isinstance(settings_json_result[key], type(self.settings_dict_example[key])):
                        logs.debug(f"Тип значения {value} - {type(value)} отличается от settings_dict_example {settings_json_result[key]} - {type(settings_json_result[key])}.")
                        settings_json_result[key] = value

        if len(settings_json_result.get("backup_folders")) == 0:
            logs.error(f"Не заполнен параметр backup_folders.")            
            exit(505)

        self.settings_json_result = settings_json_result
            
    def _load_settings(self):
        self._verify_settings()
        result = self._verify_folders()

        if self.settings_json_result != self.settings_json_result_:
            with open(self.settings_path, 'w+') as file:
                json.dump(self.settings_json_result, file, indent=4, ensure_ascii=False)
            logs.info(f"Json в папке был с ошибками, программа их исправила и сохранила новый json!")

        if result:
            return self.settings_json_result
        logs.error(f"Проверьте доступ к папкам!")
        exit(400)