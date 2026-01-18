"""
Модуль для роботи з API Hromada GetEconomyList (список громад)
"""
import requests
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from config import Config
from auth import VkursiAuth


class HromadaEconomyAPI:
    """Клас для роботи з API Hromada GetEconomyList"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Ініціалізація класу Hromada Economy API
        
        Args:
            token: Токен авторизації (якщо None, береться з .env або виконується авторизація)
        """
        self.config = Config()
        self.base_url = self.config.BASE_URL
        self.auth = VkursiAuth()
        
        # Отримуємо токен
        if token:
            self.token = token
        else:
            self.token = self.auth.get_token()
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Отримати заголовки для API запитів
        
        Returns:
            Словник з заголовками
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
    
    def _handle_response(self, response: requests.Response) -> Optional[Dict[str, Any]]:
        """
        Обробити відповідь API
        
        Args:
            response: Об'єкт відповіді requests
            
        Returns:
            Словник з даними або None у разі помилки
        """
        if response.status_code == 401:
            print("Токен недійсний або закінчився термін дії. Отримую новий токен...")
            new_token = self.auth.authorize()
            if new_token:
                self.token = new_token
                print("Отримано новий токен. Повторіть запит.")
            return None
        elif response.status_code == 200:
            try:
                return response.json()
            except ValueError:
                print("Помилка: не вдалося розпарсити JSON відповідь")
                return None
        else:
            print(f"Помилка API: {response.status_code}")
            print(f"Відповідь: {response.text}")
            return None
    
    def get_economy_list(self, date_from: str = "", date_to: str = "") -> Optional[Dict[str, Any]]:
        """
        Отримати список громад (GetEconomyList)
        
        Args:
            date_from: Дата початку періоду (за замовчуванням пустий рядок)
            date_to: Дата кінця періоду (за замовчуванням пустий рядок)
            
        Returns:
            Словник з даними списку громад або None у разі помилки
        """
        endpoint = f"{self.base_url}/api/1.0/Hromada/GetEconomyList"
        
        # Перевіряємо наявність токену
        if not self.token:
            print("Токен не знайдено. Виконую авторизацію...")
            self.token = self.auth.authorize()
            if not self.token:
                print("Помилка: не вдалося отримати токен")
                return None
        
        # Формуємо тіло запиту
        payload = {
            "dateFrom": date_from,
            "dateTo": date_to
        }
        
        try:
            # Виконуємо POST запит
            response = requests.post(
                endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            return self._handle_response(response)
            
        except requests.exceptions.RequestException as e:
            print(f"Помилка під час виконання запиту: {e}")
            return None
    
    def save_economy_list_to_file(self, economy_data: Dict[str, Any], 
                                  output_dir: str = "output") -> Optional[str]:
        """
        Зберегти дані списку громад у структурований JSON файл
        
        Args:
            economy_data: Дані списку громад для збереження
            output_dir: Директорія для збереження файлів (за замовчуванням "output")
            
        Returns:
            Шлях до збереженого файлу або None у разі помилки
        """
        if not economy_data:
            print("Помилка: немає даних для збереження")
            return None
        
        try:
            # Створюємо директорію якщо вона не існує
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Отримуємо список громад з даних
            data_list = economy_data.get("data", [])
            
            # Формуємо загальну назву (якщо є кілька громад)
            hromada_names = []
            if data_list:
                for item in data_list[:5]:  # Перші 5 для прикладу в назві
                    name = item.get("name")
                    if name:
                        hromada_names.append(str(name))
            
            hromada_name_suffix = "_".join(hromada_names[:2]) if hromada_names else "list"
            if len(hromada_names) > 2:
                hromada_name_suffix += f"_and_{len(data_list)}_more"
            
            # Формуємо ім'я файлу з датою
            current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"hromada_economy_{hromada_name_suffix}_{current_date}.json"
            # Обмежуємо довжину назви файлу
            if len(filename) > 200:
                filename = f"hromada_economy_list_{current_date}.json"
            
            filepath = output_path / filename
            
            # Створюємо структурований JSON з метаданими
            structured_data = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "description": f"Список громад (GetEconomyList). Файл створено {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. Кількість записів: {len(data_list)}",
                    "total_records": len(data_list)
                },
                "data": economy_data.get("data", []),
                "response_info": {
                    k: v for k, v in economy_data.items() if k != "data"
                }
            }
            
            # Зберігаємо у JSON файл з красивим форматуванням
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(structured_data, f, ensure_ascii=False, indent=2)
            
            print(f"Дані збережено у файл: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Помилка збереження файлу: {e}")
            return None
    
    def _handle_swot_response(self, response: requests.Response) -> Optional[Dict[str, Any]]:
        """
        Обробити відповідь API для SWOT звіту (з різними статусами)
        
        Args:
            response: Об'єкт відповіді requests
            
        Returns:
            Словник з даними або None у разі помилки
        """
        status_code = response.status_code
        
        try:
            response_data = response.json()
            
            # Діагностика: виводимо структуру відповіді для відлагодження
            print(f"\nДіагностика відповіді API (статус {status_code}):")
            print(f"Ключі в відповіді: {list(response_data.keys())}")
            
            # Статус 403 - не вистачає прав
            if status_code == 403:
                error_msg = response_data.get("ErrorMessage", "Не вистачає прав на операцію")
                print(f"Помилка {status_code}: {error_msg}")
                return {
                    "status": status_code,
                    "data": None,
                    "errorMessage": error_msg,
                    "success": False
                }
            
            # Статус 200 - успіх або дані не знайдено
            if status_code == 200:
                # Перевіряємо різні варіанти назв полів (Data, data)
                data = response_data.get("Data") or response_data.get("data")
                error_msg = response_data.get("ErrorMessage") or response_data.get("errorMessage")
                
                # Якщо дані не знайдено, перевіряємо всю відповідь
                if data is None:
                    print("Дані не знайдено в полі 'Data' або 'data'")
                    print(f"Повна відповідь API: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                
                if error_msg:
                    print(f"Попередження: {error_msg}")
                    return {
                        "status": status_code,
                        "data": data,
                        "errorMessage": error_msg,
                        "success": data is not None,
                        "raw_response": response_data  # Додаємо повну відповідь для діагностики
                    }
                else:
                    return {
                        "status": status_code,
                        "data": data,
                        "errorMessage": None,
                        "success": data is not None,
                        "raw_response": response_data  # Додаємо повну відповідь для діагностики
                    }
            
            # Статус 400 - помилка в запиті
            if status_code == 400:
                error_msg = response_data.get("ErrorMessage", "Помилка запиту")
                print(f"Помилка {status_code}: {error_msg}")
                return {
                    "status": status_code,
                    "data": None,
                    "errorMessage": error_msg,
                    "success": False
                }
            
            # Інші статуси
            print(f"Невідомий статус: {status_code}")
            print(f"Відповідь: {response.text}")
            return None
            
        except ValueError:
            print("Помилка: не вдалося розпарсити JSON відповідь")
            print(f"Сира відповідь: {response.text}")
            return None
    
    def get_swot_report(self, register_id: str) -> Optional[Dict[str, Any]]:
        """
        Отримати SWOT звіт громади (статистика громади)
        
        Args:
            register_id: ID реєстрації громади
            
        Returns:
            Словник з даними SWOT звіту або None у разі помилки
        """
        if not register_id or not register_id.strip():
            print("Помилка: register_id не може бути порожнім")
            return {
                "status": 400,
                "data": None,
                "errorMessage": "Вхідний параметр порожній.",
                "success": False
            }
        
        endpoint = f"{self.base_url}/api/1.0/hromada/getswot/{register_id.strip()}"
        
        # Перевіряємо наявність токену
        if not self.token:
            print("Токен не знайдено. Виконую авторизацію...")
            self.token = self.auth.authorize()
            if not self.token:
                print("Помилка: не вдалося отримати токен")
                return None
        
        try:
            # Виконуємо GET запит
            response = requests.get(
                endpoint,
                headers=self._get_headers(),
                timeout=30
            )
            
            return self._handle_swot_response(response)
            
        except requests.exceptions.RequestException as e:
            print(f"Помилка під час виконання запиту: {e}")
            return None
    
    def process_swot_statistics(self, swot_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обробити SWOT звіт і витягти основну статистику за розрізами
        
        Args:
            swot_data: Дані SWOT звіту для обробки
            
        Returns:
            Словник з обробленою статистикою
        """
        statistics = {
            "fop_companies": {
                "fop_count": 0,
                "companies_count": 0,
                "total_count": 0
            },
            "kved": {
                "kved_list": [],
                "kved_count": 0
            },
            "land_plots": {
                "count": 0,
                "total_area": 0
            },
            "objects": {
                "count": 0,
                "types": {}
            },
            "public_procurements": {
                "count": 0,
                "total_amount": 0
            }
        }
        
        # Отримуємо дані з різних місць відповіді
        raw_response = swot_data.get("raw_response", {})
        data = swot_data.get("data") or raw_response.get("Data") or raw_response.get("data")
        
        if not data:
            return statistics
        
        # Рекурсивно шукаємо дані в структурі
        def find_statistics(obj: Any, path: str = ""):
            """Рекурсивно шукаємо статистику в структурі даних"""
            if isinstance(obj, dict):
                # Шукаємо ФОП та компанії
                key_lower = path.lower()
                if "fop" in key_lower or "фоп" in key_lower:
                    if isinstance(obj.get("count"), (int, float)):
                        statistics["fop_companies"]["fop_count"] += int(obj["count"])
                if "company" in key_lower or "компані" in key_lower or "юо" in key_lower:
                    if isinstance(obj.get("count"), (int, float)):
                        statistics["fop_companies"]["companies_count"] += int(obj["count"])
                
                # Шукаємо КВЕД
                if "kved" in key_lower or "квед" in key_lower:
                    if isinstance(obj, list):
                        statistics["kved"]["kved_list"].extend(obj)
                    elif isinstance(obj, dict):
                        if "list" in obj:
                            statistics["kved"]["kved_list"].extend(obj["list"])
                        elif "items" in obj:
                            statistics["kved"]["kved_list"].extend(obj["items"])
                
                # Шукаємо земельні ділянки
                if "land" in key_lower or "земель" in key_lower or "ділянк" in key_lower:
                    if isinstance(obj.get("count"), (int, float)):
                        statistics["land_plots"]["count"] += int(obj["count"])
                    if isinstance(obj.get("area"), (int, float)):
                        statistics["land_plots"]["total_area"] += float(obj["area"])
                    if isinstance(obj.get("total_area"), (int, float)):
                        statistics["land_plots"]["total_area"] += float(obj["total_area"])
                
                # Шукаємо об'єкти
                if "object" in key_lower or "об'єкт" in key_lower or "обект" in key_lower:
                    if isinstance(obj.get("count"), (int, float)):
                        statistics["objects"]["count"] += int(obj["count"])
                
                # Шукаємо публічні закупівлі
                if "procurement" in key_lower or "закупівл" in key_lower or "тендер" in key_lower:
                    if isinstance(obj.get("count"), (int, float)):
                        statistics["public_procurements"]["count"] += int(obj["count"])
                    if isinstance(obj.get("amount"), (int, float)):
                        statistics["public_procurements"]["total_amount"] += float(obj["amount"])
                    if isinstance(obj.get("total_amount"), (int, float)):
                        statistics["public_procurements"]["total_amount"] += float(obj["total_amount"])
                
                # Рекурсивно обробляємо вкладені об'єкти
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    find_statistics(value, new_path)
            
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]"
                    find_statistics(item, new_path)
        
        # Запускаємо пошук статистики
        find_statistics(data)
        
        # Обчислюємо загальні показники
        statistics["fop_companies"]["total_count"] = (
            statistics["fop_companies"]["fop_count"] + 
            statistics["fop_companies"]["companies_count"]
        )
        statistics["kved"]["kved_count"] = len(statistics["kved"]["kved_list"])
        
        # Видаляємо дублікати КВЕДів якщо це словники
        if statistics["kved"]["kved_list"]:
            unique_kveds = []
            seen = set()
            for kved in statistics["kved"]["kved_list"]:
                if isinstance(kved, dict):
                    kved_str = str(kved)
                else:
                    kved_str = str(kved)
                if kved_str not in seen:
                    seen.add(kved_str)
                    unique_kveds.append(kved)
            statistics["kved"]["kved_list"] = unique_kveds
            statistics["kved"]["kved_count"] = len(unique_kveds)
        
        return statistics
    
    def save_swot_to_file(self, swot_data: Dict[str, Any], register_id: str,
                         output_dir: str = "output") -> Optional[str]:
        """
        Зберегти SWOT звіт у структурований JSON файл
        
        Args:
            swot_data: Дані SWOT звіту для збереження
            register_id: ID реєстрації громади
            output_dir: Директорія для збереження файлів (за замовчуванням "output")
            
        Returns:
            Шлях до збереженого файлу або None у разі помилки
        """
        if not swot_data:
            print("Помилка: немає даних для збереження")
            return None
        
        try:
            # Створюємо директорію якщо вона не існує
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Формуємо ім'я файлу з датою та register_id
            current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"hromada_swot_{register_id}_{current_date}.json"
            filepath = output_path / filename
            
            # Обробляємо SWOT дані і витягуємо статистику
            processed_statistics = self.process_swot_statistics(swot_data)
            
            # Створюємо структурований JSON з метаданими
            structured_data = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "register_id": register_id,
                    "description": f"SWOT звіт громади (registerId: {register_id}). Файл створено {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "status_code": swot_data.get("status"),
                    "success": swot_data.get("success", False)
                },
                "statistics": processed_statistics,  # Оброблена статистика
                "data": swot_data.get("data"),
                "error_message": swot_data.get("errorMessage"),
                "response_info": {
                    "status": swot_data.get("status"),
                    "success": swot_data.get("success", False)
                },
                "raw_response": swot_data.get("raw_response")  # Додаємо повну відповідь API для діагностики
            }
            
            # Зберігаємо у JSON файл з красивим форматуванням
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(structured_data, f, ensure_ascii=False, indent=2)
            
            print(f"Дані збережено у файл: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Помилка збереження файлу: {e}")
            return None
