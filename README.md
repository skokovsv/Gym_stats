# Training App

### Простое десктоп-приложение для учёта тренировок и построения графиков прогресса.

## Возможности

#### Ввод данных по тренировкам:

      Дата (dd.MM.yyyy)
      Вес тела (кг)
      Жим лёжа (кг) — опционально
      Штанга бицепс (кг) — опционально

#### Сохранение и обновление данных в локальной базе SQLite

#### Отображение графика прогресса по весу и жиму в основном окне

#### Открытие отдельного окна с графиком прогресса по бицепсу

#### Отображение даты последней тренировки


## Установка зависимостей

    pip install tkcalendar peewee matplotlib

## Сборка в .exe (Windows)

### Установите PyInstaller:

    pip install pyinstaller

### Выполните команду в папке с main.py:

    pyinstaller --onefile --noconsole main.py

### Готовый .exe появится в папке dist.
