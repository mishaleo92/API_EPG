"""
Основна програма для роботи з Vkursi API
"""
import sys
from auth import VkursiAuth
from bus_climate import HromadaAPI
from hromada_economy import HromadaEconomyAPI
from config import Config


def show_menu():
    """Показати головне меню"""
    print("\n" + "=" * 50)
    print("ГОЛОВНЕ МЕНЮ")
    print("=" * 50)
    print("1. Отримати дані бізнес-клімату (getclimate)")
    print("2. Отримати список громад (GetEconomyList)")
    print("3. Отримати SWOT звіт громади (getswot)")
    print("0. Вихід")
    print("=" * 50)


def get_business_climate(token: str):
    """Функція для отримання даних бізнес-клімату"""
    print("\n--- Отримання даних бізнес-клімату ---")
    
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
        print("\nДані бізнес-клімату отримано успішно!")
        print(f"Кількість ключів у відповіді: {len(climate_data)}")
        # Виводимо перші кілька ключів для прикладу
        if climate_data:
            print("\nПерші дані з відповіді:")
            for i, (key, value) in enumerate(list(climate_data.items())[:5]):
                print(f"  {key}: {value}")
            if len(climate_data) > 5:
                print(f"  ... та ще {len(climate_data) - 5} полів")
        
        # Зберігаємо дані у JSON файл
        print("\nЗбереження даних у файл...")
        saved_file = hromada_api.save_climate_to_file(climate_data, year)
        if saved_file:
            print(f"Файл успішно збережено: {saved_file}")
    else:
        print("Помилка: не вдалося отримати дані бізнес-клімату")


def get_economy_list(token: str):
    """Функція для отримання списку громад"""
    print("\n--- Отримання списку громад (GetEconomyList) ---")
    
    # Запитуємо дати (можна залишити пустими)
    date_from = input("Введіть дату початку (YYYY-MM-DD або залиште пустим): ").strip()
    date_to = input("Введіть дату кінця (YYYY-MM-DD або залиште пустим): ").strip()
    
    economy_api = HromadaEconomyAPI(token=token)
    economy_data = economy_api.get_economy_list(date_from=date_from, date_to=date_to)
    
    if economy_data:
        data_list = economy_data.get("data", [])
        print(f"\nСписок громад отримано успішно!")
        print(f"Кількість записів: {len(data_list)}")
        
        # Виводимо перші кілька записів
        if data_list:
            print("\nПерші записи зі списку:")
            for i, item in enumerate(data_list[:5], 1):
                name = item.get("name", "Без назви")
                register_id = item.get("registerId", "N/A")
                date_create = item.get("dateCreate", "N/A")
                print(f"  {i}. Назва: {name}, ID: {register_id}, Дата: {date_create}")
            if len(data_list) > 5:
                print(f"  ... та ще {len(data_list) - 5} записів")
        
        # Зберігаємо дані у JSON файл
        print("\nЗбереження даних у файл...")
        saved_file = economy_api.save_economy_list_to_file(economy_data)
        if saved_file:
            print(f"Файл успішно збережено: {saved_file}")
    else:
        print("Помилка: не вдалося отримати список громад")


def get_swot_report(token: str):
    """Функція для отримання SWOT звіту громади"""
    print("\n--- Отримання SWOT звіту громади (getswot) ---")
    
    # Запитуємо register ID
    register_id = input("Введіть Register ID громади: ").strip()
    
    if not register_id:
        print("Помилка: Register ID не може бути порожнім")
        return
    
    economy_api = HromadaEconomyAPI(token=token)
    swot_data = economy_api.get_swot_report(register_id=register_id)
    
    if swot_data:
        status_code = swot_data.get("status")
        success = swot_data.get("success", False)
        error_msg = swot_data.get("errorMessage")
        data = swot_data.get("data")
        
        if success and data:
            print(f"\nSWOT звіт отримано успішно! (Статус: {status_code})")
            print(f"Дані містять {len(data) if isinstance(data, dict) else 'невизначено'} полів")
        elif error_msg:
            print(f"\nОтримано відповідь (Статус: {status_code})")
            print(f"Повідомлення: {error_msg}")
        else:
            print(f"\nОтримано відповідь (Статус: {status_code}), але дані відсутні")
        
        # Зберігаємо дані у JSON файл (навіть якщо є помилка)
        print("\nЗбереження даних у файл...")
        saved_file = economy_api.save_swot_to_file(swot_data, register_id)
        if saved_file:
            print(f"Файл успішно збережено: {saved_file}")
    else:
        print("Помилка: не вдалося отримати SWOT звіт")


def main():
    """Головна функція програми"""
    print("=" * 50)
    print("Vkursi API EPG - Python Client")
    print("=" * 50)
    
    config = Config()
    auth = VkursiAuth()
    
    # Перевіряємо наявність облікових даних
    email, password = config.get_credentials()
    
    if not email or not password:
        print("\nОблікові дані не знайдено в .env файлі")
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
    print("\nАвторизація...")
    token = auth.authorize()
    
    if not token:
        print("Помилка: не вдалося отримати токен")
        return
    
    print(f"Токен отримано: {token[:20]}...")
    
    # Головне меню
    while True:
        show_menu()
        try:
            choice = input("\nОберіть пункт меню: ").strip()
            
            if choice == "0":
                print("\nДо побачення!")
                break
            elif choice == "1":
                get_business_climate(token)
            elif choice == "2":
                get_economy_list(token)
            elif choice == "3":
                get_swot_report(token)
            else:
                print("Помилка: невірний вибір. Спробуйте ще раз.")
                
        except KeyboardInterrupt:
            print("\n\nПрограму перервано користувачем")
            break
        except Exception as e:
            print(f"\nПомилка: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограму перервано користувачем")
        sys.exit(0)
    except Exception as e:
        print(f"\nНеперевірена помилка: {e}")
        sys.exit(1)
