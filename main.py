


import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry

from peewee import Model, SqliteDatabase, DateField, FloatField, IntegrityError
import sys

weight_data = []
bench_data = []
date_data = []

# --- Настройка базы ---
db = SqliteDatabase('training.db')

class Training(Model):
    date        = DateField(unique=True)
    weight      = FloatField()
    bench_press = FloatField(null=True)
    biceps_z = FloatField(null=True)

    class Meta:
        database = db

# Создаём таблицу при старте
db.connect()
db.create_tables([Training])





class TrainingApp:
    def __init__(self,root):
        self.root = root
        self.root.title("Traning")
        self.root.geometry("550x600")

        self.build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        self.root.destroy()
        sys.exit()

    def build_ui(self):

        self.last_date_label = ttk.Label(self.root, text="Последняя тренировка: нет данных",
                                         font=("Helvetica", 12, "italic"))
        self.last_date_label.pack(pady=(5, 10))
        self.update_last_training_date()



        # Ввод даты
        #self.date_entry = ttk.Entry(self.root)
        ttk.Label(self.root, text="Дата:",font=("Helvetica", 16, "bold")).pack(pady=(10, 0))
        self.date_entry = DateEntry(root, width=12, year=2025, date_pattern='dd.mm.yyyy',
                        background='darkblue', foreground='white', borderwidth=2,font=("Helvetica", 12))

        # self.date_entry.insert(0, datetime.today().strftime("%d-%mm-%Y"))
        self.date_entry.pack(padx=10, pady=10)


        # Ввод веса
        ttk.Label(self.root, text="Вес (кг):",font=("Helvetica", 16, "bold")).pack(pady=(10, 0))
        self.weight_entry = ttk.Entry(self.root,font=("Helvetica", 12))
        self.weight_entry.pack(padx=10, pady=5)

        frame = ttk.Frame(self.root)
        frame.pack(pady=10,padx=20)


        # Ввод жима
        ttk.Label(frame, text="Жим лёжа (кг):",font=("Helvetica", 16, "bold")).grid(row=0, column=0, padx=10)
        self.bench_entry = ttk.Entry(frame,font=("Helvetica", 12),width=10)
        self.bench_entry.grid(row=1, column=0, padx=10)


        # Ввод бицепс
        ttk.Label(frame, text="Штанга бицепс (кг):", font=("Helvetica", 16, "bold")).grid(row=0, column=1, padx=10)
        self.biceps_entry = ttk.Entry(frame, font=("Helvetica", 12),width=10)
        self.biceps_entry.grid(row=1, column=1, padx=10)





        # Кнопки
        style = ttk.Style()
        style.configure("Big.TButton", font=("Arial", 12))

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="Сохранить", command=self.save_data,style="Big.TButton").grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Показать график", command=self.show_graph,style="Big.TButton").grid(row=0, column=1, padx=5)

        ttk.Button(btn_frame, text="График бицепса", command=self.show_biceps_graph, style="Big.TButton").grid(row=0,
                                                                                                               column=2,
                                                                                                               padx=5)

        # Область для графика
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_last_training_date(self):
        last = Training.select().order_by(Training.date.desc()).first()
        if last:
            formatted_date = last.date.strftime("%d.%m.%Y")
            self.last_date_label.config(text=f"Последняя тренировка: {formatted_date}")
        else:
            self.last_date_label.config(text="Последняя тренировка: нет данных")

    def save_data(self):
        date_str = self.date_entry.get()
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
            weight = float(self.weight_entry.get())
            bench_raw = self.bench_entry.get().strip()
            bench = float(bench_raw) if bench_raw else None
            biceps_raw = self.biceps_entry.get().strip()
            biceps = float(biceps_raw) if biceps_raw else None

            # Сохраняем или обновляем
            obj, created = Training.get_or_create(
                date=date_obj,
                defaults={'weight': weight, 'bench_press': bench,'biceps_z':biceps}
            )
            if not created:
                obj.weight = weight
                obj.bench_press = bench
                obj.biceps_z = biceps
                obj.save()

            self.weight_entry.delete(0, tk.END)
            self.bench_entry.delete(0, tk.END)
            self.biceps_entry.delete(0,tk.END)

            self.update_last_training_date()

            messagebox.showinfo("Успешно", "Данные сохранены!")
        except ValueError:
            messagebox.showerror("Ошибка", "Проверь правильность ввода!")
        except IntegrityError:
            messagebox.showerror("Ошибка БД", "Проблема при сохранении в базу.")


    def show_graph(self):
        # Читаем все записи, сортируя по дате
        query = Training.select().order_by(Training.date)
        dates = [t.date for t in query]
        weights = [t.weight for t in query]
        bench_dates = [t.date for t in query if t.bench_press is not None]
        benches = [t.bench_press for t in query if t.bench_press is not None]

        biceps_dates = [t.date for t in query if t.biceps_z is not None]
        bicepses = [t.biceps_z for t in query if t.biceps_z is not None]

        if not dates:
            messagebox.showinfo("Нет данных", "Сначала добавьте записи.")
            return

        # Рисуем
        self.ax.clear()
        self.ax.plot(dates, weights, marker='o', label='Вес')
        if benches:
            self.ax.plot(bench_dates, benches, marker='x', label='Жим лёжа')

        if bicepses:
            self.ax.plot(biceps_dates, bicepses, marker='x', label='Жим лёжа')
        self.ax.set_title("Прогресс тренировок")
        self.ax.set_xlabel("Дата")
        self.ax.set_ylabel("Кг")
        self.ax.legend()
        self.ax.grid(True)
        self.fig.autofmt_xdate()
        self.canvas.draw()

    def show_biceps_graph(self):
        # Получаем данные из БД
        query = Training.select().where(Training.biceps_z.is_null(False)).order_by(Training.date)
        if not query:
            messagebox.showinfo("Нет данных", "Нет данных по бицепсу.")
            return

        dates = [t.date for t in query]
        values = [t.biceps_z for t in query]

        # Создаём новое окно
        graph_window = tk.Toplevel(self.root)
        graph_window.title("График бицепса")
        graph_window.geometry("600x400")

        # Создаём график
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(dates, values, marker='o', color='green', label="Бицепс")
        ax.set_title("Прогресс по бицепсу")
        ax.set_xlabel("Дата")
        ax.set_ylabel("Кг")
        ax.legend()
        ax.grid(True)
        fig.autofmt_xdate()

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingApp(root)
    root.mainloop()

