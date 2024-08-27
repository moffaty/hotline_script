import json
import time
import keyboard
from pynput.mouse import Controller, Button, Listener
from pynput.keyboard import Controller as KeyboardController, Key
import threading
from pathlib import Path
p = Path('locations')
# Инициализация контроллеров мыши и клавиатуры
mouse_controller = Controller()
keyboard_controller = KeyboardController()

# Глобальная переменная для хранения координат
click_positions = []

# Функция для записи кликов
def record_click(x, y, button, pressed):
    if pressed:
        if keyboard.is_pressed('ctrl+shift'):
            print(f'Recording click at ({x}, {y}) with {button}')
            click_positions.append((x, y))

# Функция для воспроизведения последовательных кликов с учетом масштабирования и нажатия клавиши "а"
def sequential_clicks(positions):
    # Флаг для контроля завершения цикла
    stop_flag = threading.Event()

    def check_stop():
        return keyboard.is_pressed('ctrl+x')

    # Запуск потока для проверки остановки
    def monitor_stop_flag():
        while not check_stop():
            time.sleep(0.1)
        stop_flag.set()
        print('Script stopped')
    monitor_thread = threading.Thread(target=monitor_stop_flag)
    monitor_thread.start()

    # Основной цикл выполнения кликов
    while not stop_flag.is_set():
        # Зажать клавишу Shift
        keyboard_controller.press(Key.shift)
        for pos in positions:
            if not stop_flag.is_set():
                if isinstance(pos, list) and len(pos) == 2:
                    x, y = pos
                    print(f'Moving to ({x}, {y}) and clicking with Shift held down')
                    mouse_controller.position = (x, y)
                    
                    # Нажать и отпустить клавишу "а"
                    keyboard_controller.press('a')
                    time.sleep(0.01)  # Небольшая задержка перед отпусканием клавиши
                    keyboard_controller.release('a')
                    
                    time.sleep(0.01)  # Задержка между кликами для наглядности

        # Отпустить клавишу Shift
        keyboard_controller.release(Key.shift)

        # Интервал между циклами
        time.sleep(10)

    # Ожидание завершения потока мониторинга
    monitor_thread.join()

# Функция для начала записи кликов
def start_recording():
    global click_positions
    click_positions = []
    print("Recording clicks...")

    def stop_recording():
        return not keyboard.is_pressed('ctrl+shift')

    listener = Listener(on_click=record_click)
    listener.start()

    while not stop_recording():
        time.sleep(0.1)

    listener.stop()
    listener.join()

    # Сохранение кликов в JSON-файл
    with open(p / 'location_new.json', 'w') as file:
        json.dump({'pos': click_positions}, file)
    print("Clicks saved to location/location_new.json")

# Функция для отслеживания горячих клавиш
def listen_for_hotkeys():
    # Воспроизведение последовательных кликов из файла
    keyboard.add_hotkey('ctrl+1', lambda: sequential_clicks(load_positions(p / 'location1.json')))

    keyboard.add_hotkey('ctrl+2', lambda: sequential_clicks(load_positions(p / 'location2.json')))

    keyboard.add_hotkey('ctrl+3', lambda: sequential_clicks(load_positions(p / 'location3.json')))

    keyboard.add_hotkey('ctrl+4', lambda: sequential_clicks(load_positions(p / 'location4.json')))

    keyboard.add_hotkey('ctrl+4', lambda: sequential_clicks(load_positions(p / 'location5.json')))

    keyboard.add_hotkey('ctrl+4', lambda: sequential_clicks(load_positions(p / 'location6.json')))

    # Начало записи кликов по комбинации клавиш Ctrl+Shift+N
    keyboard.add_hotkey('ctrl+shift', start_recording)
    
    # Воспроизведение записанных кликов из location_new.json
    keyboard.add_hotkey('ctrl+n', lambda: sequential_clicks(load_positions(p / 'location_new.json')))

    # Блокировка выполнения до тех пор, пока не будет нажата клавиша Esc
    keyboard.wait('esc+e')

# Функция для загрузки позиций из JSON-файла
def load_positions(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get('pos', [])
    except Exception as e:
        print(f'Error reading or processing the file: {e}')
        return []

# Запуск отслеживания горячих клавиш в отдельном потоке
hotkey_thread = threading.Thread(target=listen_for_hotkeys)
hotkey_thread.start()

print("Script is running. Press Esc to stop.")

# Блокировка основного потока, пока не будет нажата клавиша Esc
hotkey_thread.join()
print("Script has stopped.")
