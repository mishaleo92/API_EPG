"""
Модуль для роботи з конфігурацією та .env файлом
"""
import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Клас для управління конфігурацією програми"""
    
    BASE_URL = "https://vkursi-api.azurewebsites.net"
    TOKEN_ENV_KEY = "VKURSI_API_TOKEN"
    EMAIL_ENV_KEY = "VKURSI_EMAIL"
    PASSWORD_ENV_KEY = "VKURSI_PASSWORD"
    
    def __init__(self):
        """Ініціалізація конфігурації та завантаження .env файлу"""
        self.env_path = Path(__file__).parent / ".env"
        load_dotenv(self.env_path)
    
    def get_token(self) -> str:
        """Отримати токен з .env файлу"""
        return os.getenv(self.TOKEN_ENV_KEY, "")
    
    def save_token(self, token: str) -> bool:
        """
        Зберегти токен в .env файл
        
        Args:
            token: Токен для збереження
            
        Returns:
            True якщо успішно збережено
        """
        try:
            env_content = []
            
            # Читаємо існуючий .env файл якщо він є
            if self.env_path.exists():
                with open(self.env_path, 'r', encoding='utf-8') as f:
                    env_content = f.readlines()
            
            # Оновлюємо або додаємо токен
            token_found = False
            for i, line in enumerate(env_content):
                if line.startswith(f"{self.TOKEN_ENV_KEY}="):
                    env_content[i] = f"{self.TOKEN_ENV_KEY}={token}\n"
                    token_found = True
                    break
            
            if not token_found:
                env_content.append(f"{self.TOKEN_ENV_KEY}={token}\n")
            
            # Зберігаємо оновлений .env файл
            with open(self.env_path, 'w', encoding='utf-8') as f:
                f.writelines(env_content)
            
            # Оновлюємо змінну середовища для поточної сесії
            os.environ[self.TOKEN_ENV_KEY] = token
            
            return True
        except Exception as e:
            print(f"Помилка збереження токену: {e}")
            return False
    
    def get_credentials(self) -> tuple[str, str]:
        """
        Отримати email та password з .env файлу
        
        Returns:
            Tuple (email, password)
        """
        email = os.getenv(self.EMAIL_ENV_KEY, "")
        password = os.getenv(self.PASSWORD_ENV_KEY, "")
        return email, password
    
    def save_credentials(self, email: str, password: str) -> bool:
        """
        Зберегти email та password в .env файл
        
        Args:
            email: Email користувача
            password: Пароль користувача
            
        Returns:
            True якщо успішно збережено
        """
        try:
            env_content = []
            
            # Читаємо існуючий .env файл якщо він є
            if self.env_path.exists():
                with open(self.env_path, 'r', encoding='utf-8') as f:
                    env_content = f.readlines()
            
            # Оновлюємо або додаємо email та password
            email_found = False
            password_found = False
            
            for i, line in enumerate(env_content):
                if line.startswith(f"{self.EMAIL_ENV_KEY}="):
                    env_content[i] = f"{self.EMAIL_ENV_KEY}={email}\n"
                    email_found = True
                elif line.startswith(f"{self.PASSWORD_ENV_KEY}="):
                    env_content[i] = f"{self.PASSWORD_ENV_KEY}={password}\n"
                    password_found = True
            
            if not email_found:
                env_content.append(f"{self.EMAIL_ENV_KEY}={email}\n")
            if not password_found:
                env_content.append(f"{self.PASSWORD_ENV_KEY}={password}\n")
            
            # Зберігаємо оновлений .env файл
            with open(self.env_path, 'w', encoding='utf-8') as f:
                f.writelines(env_content)
            
            # Оновлюємо змінні середовища для поточної сесії
            os.environ[self.EMAIL_ENV_KEY] = email
            os.environ[self.PASSWORD_ENV_KEY] = password
            
            return True
        except Exception as e:
            print(f"Помилка збереження облікових даних: {e}")
            return False
