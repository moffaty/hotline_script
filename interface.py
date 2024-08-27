import tkinter as tk
from tkinter import ttk, messagebox
from main_logic import start_recording, play_clicks, start_application, update_config, get_config, stop_all

def create_gui():
    config = get_config()

    root = tk.Tk()
    root.title(config['window']['title'])
    root.geometry(f"{config['window']['width']}x{config['window']['height']}")

    # Вкладки
    tab_control = ttk.Notebook(root)

    # Вкладка Main
    tab_main = ttk.Frame(tab_control)
    tab_control.add(tab_main, text="Main")

    # Вкладка Config
    tab_config = ttk.Frame(tab_control)
    tab_control.add(tab_config, text="Config")

    tab_control.pack(expand=1, fill="both")

    # --- Вкладка Main ---
    # Кнопка записи кликов
    record_button = ttk.Button(tab_main, text="Start Recording", command=start_recording)
    record_button.pack(pady=10)

    ttk.Button(tab_main, text="Stop", command=stop_all).pack(pady=10)

    # Кнопки воспроизведения локаций
    for idx, location in enumerate(config['locations'], start=1):
        button = ttk.Button(
            tab_main,
            text=f"Play {location}",
            command=lambda loc=location: play_clicks(loc)
        )
        button.pack(pady=5)

    # --- Вкладка Config ---
    # Настройки окна
    window_frame = ttk.LabelFrame(tab_config, text="Window Settings")
    window_frame.pack(fill="x", padx=10, pady=5)

    width_label = ttk.Label(window_frame, text="Width:")
    width_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    width_entry = ttk.Entry(window_frame)
    width_entry.insert(0, str(config['window']['width']))
    width_entry.grid(row=0, column=1, padx=5, pady=5)

    height_label = ttk.Label(window_frame, text="Height:")
    height_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    height_entry = ttk.Entry(window_frame)
    height_entry.insert(0, str(config['window']['height']))
    height_entry.grid(row=1, column=1, padx=5, pady=5)

    # Настройки кликов
    click_frame = ttk.LabelFrame(tab_config, text="Click Settings")
    click_frame.pack(fill="x", padx=10, pady=5)

    click_delay_label = ttk.Label(click_frame, text="Click Delay (s):")
    click_delay_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    click_delay_entry = ttk.Entry(click_frame)
    click_delay_entry.insert(0, str(config['click_settings']['click_delay']))
    click_delay_entry.grid(row=0, column=1, padx=5, pady=5)

    cycle_interval_label = ttk.Label(click_frame, text="Cycle Interval (s):")
    cycle_interval_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    cycle_interval_entry = ttk.Entry(click_frame)
    cycle_interval_entry.insert(0, str(config['click_settings']['cycle_interval']))
    cycle_interval_entry.grid(row=1, column=1, padx=5, pady=5)

    # Кнопка сохранения настроек
    def save_settings():
        try:
            new_config = {
                'window': {
                    'width': int(width_entry.get()),
                    'height': int(height_entry.get()),
                    'title': config['window']['title']
                },
                'click_settings': {
                    'click_delay': float(click_delay_entry.get()),
                    'cycle_interval': float(cycle_interval_entry.get())
                },
                'locations': config['locations'],
                'hotkeys': config['hotkeys'],
                'paths': config['paths']
            }
            update_config(new_config)
            messagebox.showinfo("Success", "Settings have been updated successfully!")
            root.geometry(f"{new_config['window']['width']}x{new_config['window']['height']}")
        except ValueError as ve:
            messagebox.showerror("Error", f"Invalid input: {ve}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    save_button = ttk.Button(tab_config, text="Save Settings", command=save_settings)
    save_button.pack(pady=10)

    # Запуск основного цикла приложения
    start_application()
    root.mainloop()

if __name__ == "__main__":
    create_gui()
