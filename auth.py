"""
Модуль для авторизації та отримання токену Vkursi API
"""
import requests
import json
from typing import Optional
from config import Config


class VkursiAuth:
    """Клас для авторизації в Vkursi API"""
    
    def __init__(self):
        """Ініціалізація класу авторизації"""
        self.config = Config()
        self.base_url = self.config.BASE_URL
        self.auth_endpoint = f"{self.base_url}/api/1.0/token/authorize"
    
    def authorize(self, email: Optional[str] = None, password: Optional[str] = None) -> Optional[str]:
        """
        Авторизація та отримання токену
        
        Args:
            email: Email користувача (якщо None, береться з .env)
            password: Пароль користувача (якщо None, береться з .env)
            
        Returns:
            Токен авторизації або None у разі помилки
            
        Note:
            Термін дії токену 30 хвилин
        """
        # Отримуємо облікові дані з параметрів або .env
        if email is None or password is None:
            env_email, env_password = self.config.get_credentials()
            email = email or env_email
            password = password or env_password
        
        if not email or not password:
            print("Помилка: не вказано email або password")
            print("Вкажіть облікові дані в .env файлі або передайте їх як параметри")
            return None
        
        # Формуємо тіло запиту
        payload = {
            "email": email,
            "password": password
        }
        
        # Заголовки запиту
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            # Виконуємо POST запит
            response = requests.post(
                self.auth_endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Перевіряємо статус відповіді
            if response.status_code == 200:
                response_data = response.json()
                # Шукаємо токен в різних форматах (Token, token)
                token = response_data.get("Token") or response_data.get("token")
                
                if token:
                    # Зберігаємо токен в .env файл
                    if self.config.save_token(token):
                        print("Токен успішно отримано та збережено в .env файл")
                    else:
                        print("Токен отримано, але не вдалося зберегти в .env файл")
                    
                    return token
                else:
                    print("Помилка: токен не знайдено в відповіді API")
                    print(f"Структура відповіді: {response_data}")
                    print(f"Повна відповідь: {response.text}")
                    return None
            else:
                print(f"Помилка авторизації: {response.status_code}")
                print(f"Відповідь: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Помилка під час виконання запиту: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Помилка парсингу JSON відповіді: {e}")
            return None
    
    def get_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        Отримати токен з .env або виконати авторизацію
        
        Args:
            force_refresh: Якщо True, виконує нову авторизацію навіть якщо токен є
            
        Returns:
            Токен авторизації або None
        """
        # Якщо не потрібно оновлювати, спробуємо отримати з .env
        if not force_refresh:
            token = self.config.get_token()
            if token:
                return token
        
        # Виконуємо авторизацію
        return self.authorize()
    
    def is_token_valid(self, token: Optional[str] = None) -> bool:
        """
        Перевірити чи токен дійсний (опціонально, можна використати для перевірки)
        
        Args:
            token: Токен для перевірки (якщо None, береться з .env)
            
        Returns:
            True якщо токен дійсний
        """
        if token is None:
            token = self.config.get_token()
        
        if not token:
            return False
        
        # Можна додати перевірку через API endpoint
        # Поки що просто перевіряємо наявність токену
        return len(token) > 0
