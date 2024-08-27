import json
import time
import threading
import keyboard
from pathlib import Path
from pynput.mouse import Controller, Listener
from pynput.keyboard import Controller as KeyboardController, Key

# Глобальная переменная для остановки скрипта
stop_flag = threading.Event()

# Загрузка и сохранение конфигурации
def load_config():
    with open('config.json', 'r') as config_file:
        return json.load(config_file)

def save_config(config):
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)

config = load_config()

# Инициализация контроллеров мыши и клавиатуры
mouse_controller = Controller()
keyboard_controller = KeyboardController()
locations_path = Path(config['paths']['locations_folder'])
new_location_file = config['paths']['new_location_file']

# Глобальная переменная для хранения координат
click_positions = []

# Функция для записи кликов
def record_click(x, y, button, pressed):
    if pressed:
        print(f'Recording click at ({x}, {y}) with {button}')
        click_positions.append((x, y))

# Функция для последовательного выполнения кликов
def sequential_clicks(positions):
    global stop_flag
    stop_flag.clear()  # Очистить флаг остановки перед началом нового выполнения

    def check_stop():
        return keyboard.is_pressed(config['hotkeys']['stop_script'])

    def monitor_stop_flag():
        while not check_stop() and not stop_flag.is_set():
            time.sleep(0.1)
        stop_flag.set()
        print('Script stopped')

    monitor_thread = threading.Thread(target=monitor_stop_flag)
    monitor_thread.start()

    while not stop_flag.is_set():
        keyboard_controller.press(Key.shift)
        for pos in positions:
            if stop_flag.is_set():
                break
            if isinstance(pos, (list, tuple)) and len(pos) == 2:
                x, y = pos
                print(f'Moving to ({x}, {y}) and clicking with Shift held down')
                mouse_controller.position = (x, y)
                keyboard_controller.press('a')
                time.sleep(config['click_settings']['click_delay'])
                keyboard_controller.release('a')
                time.sleep(config['click_settings']['click_delay'])
        keyboard_controller.release(Key.shift)
        time.sleep(config['click_settings']['cycle_interval'])
    monitor_thread.join()

# Запуск записи кликов в отдельном потоке
def start_recording():
    def recording():
        global click_positions
        click_positions = []
        print("Recording clicks... Press the recording hotkey again to stop.")

        def stop_recording():
            # Продолжать запись, пока снова не будет нажата комбинация клавиш для остановки
            while not keyboard.is_pressed(config['hotkeys']['start_recording']):
                time.sleep(0.1)

            return True

        listener = Listener(on_click=record_click)
        listener.start()

        while not stop_recording():
            time.sleep(0.1)

        listener.stop()
        listener.join()

        save_path = locations_path / new_location_file
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, 'w') as file:
            json.dump({'pos': click_positions}, file, indent=4)
        print(f"Clicks saved to {save_path}")

    threading.Thread(target=recording, daemon=True).start()


# Запуск последовательного кликанья в отдельном потоке
def play_clicks(file_name):
    def playback():
        positions = load_positions(file_name)
        if positions:
            sequential_clicks(positions)
        else:
            print(f"No positions found in {file_name}.json")

    threading.Thread(target=playback, daemon=True).start()

# Загрузка позиций из файла
def load_positions(file_name):
    file_path = locations_path / f"{file_name}.json"
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get('pos', [])
    except Exception as e:
        print(f'Error reading or processing the file {file_path}: {e}')
        return []

# Обновление и получение конфигурации
def update_config(new_config):
    global config
    config.update(new_config)
    save_config(config)
    print("Configuration updated and saved.")

def get_config():
    return config

# Остановка всех потоков
def stop_all():
    global stop_flag
    stop_flag.set()
    print("All scripts stopped.")

# Регистрация горячих клавиш
def register_hotkeys():
    # keyboard.add_hotkey(config['hotkeys']['start_recording'], start_recording)
    keyboard.add_hotkey(config['hotkeys']['play_new_location'], lambda: play_clicks(new_location_file.replace('.json', '')))
    keyboard.add_hotkey(config['hotkeys']['stop_script'], stop_all)

    for idx, location in enumerate(config['locations'], start=1):
        hotkey = config['hotkeys'].get(f'play_location_{idx}')
        if hotkey:
            keyboard.add_hotkey(hotkey, lambda loc=location: play_clicks(loc))

    keyboard.wait(config['hotkeys']['exit_application'])

# Запуск основного приложения
def start_application():
    hotkeys_thread = threading.Thread(target=register_hotkeys, daemon=True)
    hotkeys_thread.start()
