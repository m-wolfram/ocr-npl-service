# python_ai

Структура проекта имеет следующий вид:
    logs - папка хранения файлов лога;
    modules - папка хранения модулей проекта(модуль распознавания, модуль ner и др.);
    project_data - папка хранения файлов, связанных с проектом:
      - папка requests_notebook хранит в себе jupyter тетрадку отправки запросов к сервису и pages - примеры изображений;
      - папка traineddata хранит в себе модели распознавания tesseract;
      - docker_run_cmd.txt - содержит в себе пример команды запуска проекта в контейнеризированном виде;
      - requirements.txt - содержит в себе информацию о python зависимостях проекта;
      - todo.txt - содержит в себе информацию о незаконченных частях проекта и идеях.
    uploaded data - папка хранения файлов, загруженных на сервер через запросы;
    utils - папка хранения библиотек, связанных с работой веб-сервиса;
    
    Dockerfile - файл сборки образа под проект;
    settings.py - настройки веб-сервиса;
    web_service.py - главный файл запуска веб-сервиса.

Структура модуля распознавания:
  temp - хранит в себе временные файлы модуля;
  settings - настройки модуля.
  
Структура модуля NER(аналогично модулю распознавания):
  settings - настройки модуля.

В проекте представлены файлы .gitkeep, хранящиеся в потенциально-пустых папках для корректной загрузки в гит.
