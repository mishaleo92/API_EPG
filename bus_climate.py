"""
Модуль для роботи з API бізнес-клімату (Hromada getclimate)
"""
import requests
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from config import Config
from auth import VkursiAuth


class HromadaAPI:
    """Клас для роботи з API Hromada"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Ініціалізація класу Hromada API
        
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
            # Отримуємо новий токен
            new_token = self.auth.authorize()
            if new_token:
                self.token = new_token
                # Можна повторити запит, але поки що просто повертаємо None
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
    
    def get_climate(self, year: int = 1) -> Optional[Dict[str, Any]]:
        """
        Отримати дані бізнес-клімату
        
        Args:
            year: Рік для отримання даних (за замовчуванням 1)
            
        Returns:
            Словник з даними бізнес-клімату або None у разі помилки
            
        Example:
            >>> api = HromadaAPI()
            >>> data = api.get_climate(year=2023)
        """
        endpoint = f"{self.base_url}/api/1.0/Hromada/getclimate"
        
        # Перевіряємо наявність токену
        if not self.token:
            print("Токен не знайдено. Виконую авторизацію...")
            self.token = self.auth.authorize()
            if not self.token:
                print("Помилка: не вдалося отримати токен")
                return None
        
        # Формуємо тіло запиту
        payload = {
            "year": year
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
    
    def refresh_token(self) -> bool:
        """
        Оновити токен авторизації
        
        Returns:
            True якщо токен успішно оновлено
        """
        new_token = self.auth.authorize()
        if new_token:
            self.token = new_token
            return True
        return False
    
    def save_climate_to_file(self, climate_data: Dict[str, Any], year: int, 
                            output_dir: str = "output") -> Optional[str]:
        """
        Зберегти дані бізнес-клімату у структурований JSON файл
        
        Args:
            climate_data: Дані бізнес-клімату для збереження
            year: Рік даних
            output_dir: Директорія для збереження файлів (за замовчуванням "output")
            
        Returns:
            Шлях до збереженого файлу або None у разі помилки
        """
        if not climate_data:
            print("Помилка: немає даних для збереження")
            return None
        
        try:
            # Створюємо директорію якщо вона не існує
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Формуємо ім'я файлу з датою та роком
            current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"climate_year_{year}_{current_date}.json"
            filepath = output_path / filename
            
            # Створюємо структурований JSON з метаданими
            structured_data = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "year": year,
                    "description": f"Дані бізнес-клімату за {year} рік. Файл створено {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                },
                "data": climate_data
            }
            
            # Зберігаємо у JSON файл з красивим форматуванням
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(structured_data, f, ensure_ascii=False, indent=2)
            
            print(f"Дані збережено у файл: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Помилка збереження файлу: {e}")
            return None