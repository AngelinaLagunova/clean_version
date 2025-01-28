Данный проект это транслятор подмножества языка С++ в эквивалентное подмножество языка Java. 
# Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/AngelinaLagunova/clean_version.git
cd api_final_yatube
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
```
Если у вас Linux/macOS
```
source env/bin/activate
```
Если у вас windows
```
source env/scripts/activate
```
Далее
```
python3 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Далее запустите файл translator.py, это можно сделать из командной строки
```
python3 translator.py
```
Чтобы вывести дерево разбора и результат работы программы в консоль, впишите код на С++ в файл program.cpp и запустите файл debug.py
```
python3 debug.py
```
