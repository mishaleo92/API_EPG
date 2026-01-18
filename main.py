"""
Основна програма для роботи з Vkursi API
"""
import sys
from auth import VkursiAuth
from hromada import HromadaAPI
from config import Config


def main():
    """Головна функція програми"""
    print("=" * 50)
    print("Vkursi API EPG - Python Client")
    print("=" * 50)
    print()
    
    config = Config()
    auth = VkursiAuth()
    
    # Перевіряємо наявність облікових даних
    email, password = config.get_credentials()
    
    if not email or not password:
        print("Облікові дані не знайдено в .env файлі")
        print("Введіть ваші облікові дані:")
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        
        if email and password:
            config.save_credentials(email, password)
            print("Облікові дані збережено в .env файл")
        else:
            print("Помилка: облікові дані не вказано")
            return
    
    # Авторизація та отримання токену
    print("\n1. Авторизація...")
    token = auth.authorize()
    
    if not token:
        print("Помилка: не вдалося отримати токен")
        return
    
    print(f"Токен отримано: {token[:20]}...")
    
    # Приклад використання Hromada API
    print("\n2. Отримання даних бізнес-клімату...")
    
    # Запитуємо рік у користувача
    while True:
        try:
            year_input = input("Введіть рік для отримання даних бізнес-клімату: ").strip()
            year = int(year_input)
            if year > 0:
                break
            else:
                print("Помилка: рік повинен бути більше 0")
        except ValueError:
            print("Помилка: введіть коректне число")
        except KeyboardInterrupt:
            print("\nОперацію перервано")
            return
    
    hromada_api = HromadaAPI(token=token)
    climate_data = hromada_api.get_climate(year=year)
    
    if climate_data:
        print("Дані бізнес-клімату отримано успішно!")
        print(f"Кількість ключів у відповіді: {len(climate_data)}")
        # Виводимо перші кілька ключів для прикладу
        if climate_data:
            print("\nПерші дані з відповіді:")
            for i, (key, value) in enumerate(list(climate_data.items())[:5]):
                print(f"  {key}: {value}")
            if len(climate_data) > 5:
                print(f"  ... та ще {len(climate_data) - 5} полів")
    else:
        print("Помилка: не вдалося отримати дані бізнес-клімату")
    
    print("\n" + "=" * 50)
    print("Програма завершена")
    print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограму перервано користувачем")
        sys.exit(0)
    except Exception as e:
        print(f"\nНеперевірена помилка: {e}")
        sys.exit(1)
