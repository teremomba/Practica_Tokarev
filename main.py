# main.py

"""
Приложение для редактирования изображений с единой панелью инструментов,
автоматически расширяющее окно под размер загруженного изображения.
"""

import logging
import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


class ImageEditorApp:
    """
    GUI-приложение для базовой обработки изображений:
    загрузка, видео-кадр, каналы, маскирование, резкость и рисование.
    """

    def __init__(self, root: tk.Tk):
        """
        Инициализирует окно приложения, настраивает панель инструментов и область отображения.

        Args:
            root (tk.Tk): Корневое окно Tkinter.
        """
        self.root = root
        self.root.title("Редактор Изображений")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        self.img: np.ndarray | None = None
        """Текущее изображение в формате numpy RGB массива."""
        self.tk_img: ImageTk.PhotoImage | None = None
        """PhotoImage для отображения в Tkinter."""

        # Единая панель инструментов
        self.toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self._create_toolbar()

        # Область показа изображения
        self.canvas = tk.Label(self.root, bg="gray")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        logger.info("Приложение запущено")

    def _create_toolbar(self):
        """
        Создаёт единую панель инструментов с выпадающими меню и кнопками.

        Меню:
            - Файл: Загрузить, С веб-камеры
            - Канал: Red, Green, Blue
        Кнопки:
            - Маска по красному
            - Резкость
            - Рисовать прямоугольник
        """
        # Меню "Файл"
        file_mb = tk.Menubutton(self.toolbar, text="Файл", relief=tk.RAISED)
        file_menu = tk.Menu(file_mb, tearoff=False)
        file_menu.add_command(label="Загрузить…", command=self.open_file)
        file_menu.add_command(label="С веб-камеры", command=self.capture_from_cam)
        file_mb.config(menu=file_menu)
        file_mb.pack(side=tk.LEFT, padx=4)

        # Меню "Канал"
        chan_mb = tk.Menubutton(self.toolbar, text="Канал", relief=tk.RAISED)
        chan_menu = tk.Menu(chan_mb, tearoff=False)
        chan_menu.add_command(label="Red", command=lambda: self.show_channel("R"))
        chan_menu.add_command(label="Green", command=lambda: self.show_channel("G"))
        chan_menu.add_command(label="Blue", command=lambda: self.show_channel("B"))
        chan_mb.config(menu=chan_menu)
        chan_mb.pack(side=tk.LEFT, padx=4)

        # Обычные кнопки
        btn_specs = [
            ("Маска по красному", self.red_mask),
            ("Резкость", self.sharpen),
            ("Рисовать прямоугольник", self.draw_rectangle),
        ]
        for text, cmd in btn_specs:
            tk.Button(self.toolbar, text=text, command=cmd).pack(side=tk.LEFT, padx=4)

    def _update_display(self, img_array: np.ndarray):
        """
        Обновляет область отображения новым изображением и подгоняет размер окна.

        Args:
            img_array (np.ndarray): RGB-изображение для отображения.
        """
        img = Image.fromarray(img_array)
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.config(image=self.tk_img)

        # Обновляем окно и измеряем размеры изображения
        self.root.update_idletasks()
        img_w, img_h = self.tk_img.width(), self.tk_img.height()
        toolbar_h = self.toolbar.winfo_height()

        # Вычисляем новый размер окна с учётом отступов
        pad_x = 20  # отступ слева/справа
        pad_y = 20  # отступ сверху/снизу
        new_w = img_w + pad_x
        new_h = img_h + toolbar_h + pad_y
        self.root.geometry(f"{new_w}x{new_h}")

    def open_file(self):
        """
        Открывает диалог выбора файла и загружает изображение через PIL,
        поддерживает пути с кириллицей.
        """
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg")]
        )
        if not path:
            return
        try:
            pil_img = Image.open(path).convert("RGB")
            self.img = np.array(pil_img)
            logger.info(f"Изображение загружено: {path}")
            self._update_display(self.img)
        except Exception as e:
            logger.error(f"Ошибка загрузки: {e}")
            messagebox.showerror("Ошибка", "Не удалось загрузить изображение.")

    def capture_from_cam(self):
        """
        Захватывает один кадр с веб-камеры и отображает его.
        """
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            messagebox.showerror("Ошибка", "Не удалось открыть веб-камеру")
            return
        ret, frame = cap.read()
        cap.release()
        if not ret:
            messagebox.showerror("Ошибка", "Не удалось захватить кадр")
            return
        self.img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        logger.info("Снимок с веб-камеры сделан")
        self._update_display(self.img)

    def show_channel(self, channel: str):
        """
        Показывает выбранный канал изображения (R, G или B).

        Args:
            channel (str): Одна из строк "R", "G", "B".
        """
        if self.img is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение")
            return
        idx = {"R": 0, "G": 1, "B": 2}[channel]
        ch = self.img[:, :, idx]
        rgb = np.stack([ch] * 3, axis=-1)
        logger.info(f"Показан канал {channel}")
        self._update_display(rgb)

    def red_mask(self):
        """
        Формирует и показывает чёрно-белую маску областей,
        где красный канал превышает указанный порог.
        """
        if self.img is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение")
            return
        thresh = simpledialog.askinteger("Порог", "Задайте порог (0–255)", minvalue=0, maxvalue=255)
        if thresh is None:
            return
        mask = (self.img[:, :, 0] > thresh).astype(np.uint8) * 255
        rgb = np.stack([mask] * 3, axis=-1)
        logger.info(f"Маска по красному > {thresh}")
        self._update_display(rgb)

    def sharpen(self):
        """
        Применяет оператор повышения резкости к текущему изображению.
        """
        if self.img is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение")
            return
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        sharp = cv2.filter2D(self.img, -1, kernel)
        logger.info("Применён фильтр резкости")
        self._update_display(sharp)

    def draw_rectangle(self):
        """
        Рисует синий контур прямоугольника по координатам, введённым пользователем.
        """
        if self.img is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение")
            return
        x1 = simpledialog.askinteger("X1", "Введите X1", minvalue=0)
        y1 = simpledialog.askinteger("Y1", "Введите Y1", minvalue=0)
        x2 = simpledialog.askinteger("X2", "Введите X2", minvalue=0)
        y2 = simpledialog.askinteger("Y2", "Введите Y2", minvalue=0)
        if None in (x1, y1, x2, y2):
            return
        img_copy = self.img.copy()
        cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 0, 255), thickness=2)
        logger.info(f"Нарисован прямоугольник: ({x1},{y1})->({x2},{y2})")
        self._update_display(img_copy)

    def run(self):
        """
        Запускает главный цикл обработки событий Tkinter.
        """
        self.root.mainloop()


if __name__ == "__main__":
    app = ImageEditorApp(tk.Tk())
    app.run()
