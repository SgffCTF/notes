# notes | CTF Attack-Defense service

notes представляет из себя сервис для CTF формата Attack-Defense, который содержит чекер совместимый с жюрейной системой [ForcAD](https://github.com/pomo-mondreganto/ForcAD).

## Описание

Сервис представляет из себя обычный CRUD заметок с возможностью создания приватных/публичных заметок и добавления к ним файлов.

## Запуск

```bash
cd service
docker compose up --build -d
```

## Уязвимости

Сервис содержит 3 уязвимости. Разбор уязвимостей и эксплойты можно посмотреть [тут](writeup/).

## Чекер

Чекер находится [тут](checker/). Был протестирован на проверяющей системы [ForcAD](https://github.com/pomo-mondreganto/ForcAD).