# Writeup | notes

## Path traversal в эндпоинте /download

### Описание

При скачивании файлов можно заметить, что название файла передаётся в GET параметре. Стандартный Path Traversal через ../ здесь не проходит из-за защиты:
```bash
if '../' in str(requested_file):
    flash('malicious', 'error')
    return redirect(url_for('index'))
```
Но из-за особенности конкатенации путей библиотеки pathlib можно получить файл, указав полный путь:
```bash
curl http://10.10.1.2:5000/download?filename=/etc/passwd
root:x:0:0:root:/root:/bin/sh
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
...
```

Так как БД используется sqlite3, то можно её получить одним запросом.

[Эксплойт](./sploits/sploit1.py)

### Патч

Достаточно использовать функцию `send_from_directory` вместо `send_file`, так как она не позволит выйти из директории и будет считать директорию, переданную первым аргументов, как корневую.
```python
return send_from_directory(upload_dir, requested_file, as_attachment=True)
```

## Захардкоженный ключ подписи сессии

### Описание

Можно заметить захардкоженный ключ подписи сессии. Данный ключ одинаковый у всех команд, что позволяет подписать сессию от имени любого пользователя сервиса.
```python
app.secret_key = 'nigga'
```

[Эксплойт](./sploits/sploit2.py)

### Патч

Поменять ключ или сделать его рандомным.
```python
import string
from random import choice


app.secret_key = ''.join([choice(string.ascii_letters) for _ in range(16)])
```

## IDOR на редактирование/получение заметки в эндпоинте /edit/<note_id>

### Описание

В сервисе присутсвует idor, который позволяет редактировать/просматривать заметку по id. Получив id из attack data мы можем отредактировать видимость заметки с помощью POST запроса, сделав её публичной, и прочитать на основной странице либо же через GET запрос напрямую получить заметку, так как эндпоинт не содержит проверки на оба метода.

[Эксплойт](./sploits/sploit3.py)

### Патч

```python
if note is None or note['user_id'] != session['user_id']:
    flash('Вы не можете редактировать эту заметку!', 'error')
    return redirect(url_for('index'))
```
