# python_ai

По доработкам смотреть в todo.txt в project_data
Также есть версия с загруженной в образ моделью deeppavlov, но в гит она не влазит.
Алгоритм такой:
    Модель загружена в образ и в ходе запуска проекта скачивать её не нужно.
    В ходе запуска проверяется, происходит ли запуск внутри контейнера, и в случае запуска внутри, модель не скачивается.

### Выполнены следующие задания:
    
#### 1. Извлечение текстового слоя.
    Выполнено основное задание и дополнительное.
    
    Используется движок распознавания tesseract OCR.
    Сделано в виде модуля распознавания в папке modules.recognition.
    Вызывается главная функция modules.recognition.recognize_image(<путь до изображения>).
    
    В настройках модуля можно указать:
    
    size: размер изображения для интерполяции в ходе распознавания,
    lang: язык распознавания(по умолчанию eng т.к. примеры документов на английском),
    config: конфиг вызова тессеракта(указан 11 режим сегментации как стандартный вид сегментации извлечения текста).
            Можно в дальнейшем расширять логику, например путём распознавания с разными конфигами.
            В таком случае этот параментр уберётся.
    sep: разделитель для объединения распознанных слов(по умолчанию указан пробел).
    debug: включение/выключение режима отладки модуля.
           В отладочном режиме, в папку модуля temp сохраняется изображение с отрисовкой положения распознанных слов.
           Сохраняется только последнее отрисованное изображение, остальные удаляются при сохранении новой.

#### 2. Поиск объектов.
    Выполнено в виде модуля-заглушки в modules для использования в задании 5.

    Это задание можно выполнить путём обучения модели object detection yolo + darknet.
    Я бы обучил https://pjreddie.com/darknet/yolo/.
    Дообучением готовой модели или обучением с 0.

    Разметка прилагается к заданию.
    Её можно преобразовать под нужный формат и использовать в качестве входных данных для обучения или дообучения модели вместе с картинками.
    Типы объектов sign и logo.
    Далее оформил бы в виде отдельного модуля аналогично другим модулям.

#### 3. Классификация.
    Выполнено в виде модуля-заглушки в modules для использования в задании 5.
    
#### 4. Извлечение значимых данных.
    Выполнено основное задание и дополнительное двумя разными способами:
    - При помощи NER Natasha,
    - и NER deeppavlov.
    
    Дополнительное задание реализовано в виде пайплайна извлечения сущностей из изображения.
    Пайплайн вызывает функции из отдельных модулей, обрабатывает и объединяет ответы.
    Также пайплайн формирует финальный ответ дополнительного задания.
    Пайплайн представлен в <папка проекта>/pipelines/ner_image_pipeline.py.
    Вызывается главная функция запуска пайплайна run_ner_image_pipeline(<путь до изображения>).
    
    Задание выполнено в виде двух модулей в папках modules.ner_natasha и modules.ner_deeppavlov.
    Реализована работа как с Natasha, так и с Deeppavlov.
    Вызываются главные функции модулей ner_text(<текст>).
    
    NER Natasha показала себя лучше при извлечении сущностей из русскоязычного текста.
    Deeppavlov оказался более точным(по статистике в интернете в сравнении с Natasha и в ходе тестов).
    Используется именно он по умолчанию.
    
    Deeppavlov занимает много памяти и могут быть проблемы с его запуском:
        В проекте можно выбрать движок распознавания.
        Для этого нужно поменять значения в файлах на "Natasha":
        
            <папка проекта>/pipelines/ner_image_pipeline в функции get_entities_from_ocr(..),
            <папка проекта>/utils/ner_requests_processing в функции ner_txt(..),
            
            переменные ner_engine_type и engine_type.
        Можно указать один из вариантов: "DP" и "Natasha".
    Можно отключить использование модуля с deeppavlov путём комментирования его импортирования в эти файлы.
    
    При первом запуске проекта скачивается модель(~2гб).
    Предотвращение повторного скачивания при запуске в контейнере реализуется путём сохранения файлов моделей в образ.
    
    Отдельно использование deeppavlov представлено на в Google Colab(этот же код используется в модуле ner_deeppavlov):
        https://colab.research.google.com/drive/1pd5u8no31VtOSTI0ak7YmoZuHvOzxPL1?usp=sharing.
    
    В настройках модуля deeppavlov можно выбрать модель для ner и необходимость её скачивания.
    Также можно включить или отключить режим отладки модуля.
    Для модуля ner_natasha также предусмотрено включение и отключение режима отладки.
    
#### 5. Pipeline обработки документов.
    Задание выполнено с использованием модулей-заглушек классификации и извлечения объектов.
    
    Заглушки представлены в виде заготовленного заранее ответа нужного формата.
    
    Пайплайн выполнен в виде последовательного запуска функций в файле:
        <папка проетка>/pipelines/document_processing_pipeline.py.
    Вызывается главная функция run_document_pipeline(<список путей изображений до документа>).
    
    Формат ответа следующий:
    
    {
        "text": объединенный текст страниц документа,
        "pages": [
            {
                "index": номер страницы,
                "text": извлеченный из страницы текст,
                "objects": [
                    {
                        "type": тип объека "logo" или "sign",
                        "position": {
                            "left": позиция верхнего левого угла объекта по x,
                            "top": позиция верхнего левого угла объекта по y,
                            "width": ширина объекта,
                            "height" высота объекта
                        }
                    },
                    ...
                ],
                "info": {
                    "width": ширина страницы,
                    "height": высота страницы,
                    "type": класс страницы "main" или "other"
                },
                "facts": [
                    {
                        "text": текст сущности,
                        "tag": тэг сущности вида "PERSON", "DATE", "MONEY", "ORGANIZATION" или "LOCATION",
                        "tokens": [
                            {
                                "text": текст токена,
                                "offset" позиция первого символа токена относительно начала текста
                            },
                            ...
                        ]
                    },
                    ...
                ] или None, если класс страницы не "main"
            },
            ...
        ]
    }

    Ответ содержит в себе информацию о каждой странице и общий объединенный текст.

    Некоторые шаги пайплайна можно распараллелить.
    Для этого всё подготовлено и в коде есть комментарии про это.

#### ***. Реализация проекта.
    Сам проект реализован в виде веб-сервиса на Flask и waitress.
    В самом веб-сервисе ничего не указывается, значения для ip адреса и порта берутся из настроек.

    В проекте реализована проверка на запуск внутри контейнера через переменную среды в docker образе.
    В случае запуска внутри контейнера, присваивается локальный адрес контейнера, игнорируя ip адрес из настроек.
    При обращении ко внешнему адресу и порту веб-сервиса, запросы перенаправляются на этот адрес.
    
    Также реализовано логирование в файл, сохраняемый в папку logs и в консоль.
    Файл является перезаписываемым по достижении определенного размера.
    Максимальный размер файла и число хранимых файлов указывается в настройках.
    Также в настройках можно указать уровень логирования(по умолчанию debug).
    Ошибки сервиса логируются c трейсбэком.

    Реализована обработка 4 запросов по выполненным заданиям.
    Общая структура обработки запросов следующая:
        1. В web_service.py происходит обработка запроса, извлекается его тело.
        2. Тело запроса направляется в отдельный класс обработки запроса определенного типа в service_requests.
        3. В классе происходит подготовка полученных данных для обработки модулями и/или пайплайнами, формируется ответ.
           Ответ формируется в виде json и возвращается обратно в web_service.py.
        5. Веб-сервис отправляет полученный json обратно клиенту.
    
    Файлы, отправляемые в запросах сохраняются в папку uploaded_data:
    Каждому запросу, подразумевающему сохранение файлов, присваивается уникальный идентификатор uuid.
    Для файлов, связанных с обработкой запроса, создается отдельная папка с идентификатором.

    Функцинал сервиса реализован в виде отдельных модулей, хранимых в modules.
    Пайплайны расположены в папке pipelines и взаимодействуют с модулями из modules.

    В папке utils можно привести порядок, организовать обработку запросов в виде структуры классов.

    Падение сервиса обрабатываются в каждом методе обработки запросов и возвращают ответ об ошибке формата:
    {
        "error": текст ошибки,
        "time": время возникновения ошибки
    }
    
    Прокомментировано большинство частей кода.
    Не нужные для выгрузки в гит файлы прописаны в .gitignore.
    В потенциально-пустых папках находятся файлы .gitkeep для сохранения их в гит-репозитории.

#### ******. Дополнительно сделана запаковка проекта в docker-контейнер.
    В корне проекта находится файл Dockerfile, создающий образ под проект.
    Команда сборки и запуска проекта в виде контейнера записана в <папка проекта>/project_data/docker_run_cmd.txt.
    В ней нужно поменять путь до папки с проектом в параметре -v до двоеточия.
    
    Реализована возможность запуска jupyter сервера на базе образа с окружением.
    Команда запуска записана в <папка проекта>/notebooks/run_jupyter_notebook.txt.
    В ней, аналогично запуску проекта, необходимо поменять путь до папки notebooks в параметре -v.
    
    Файлы проекта пробрасываются в образ.
    Можно реализовать путём их копирования внутрь образа при создании. 
    При этом, так менее удобно в ходе разработки.

### Запросы к сервису.
    Запросы к сервису находятся в тетрадке <папка проекта>/project_data/requests_notebook/directum_ai_requests.ipynb
    Пути до примеров берутся из локальной папки и уже прописаны в коде отправки запроса.

### Структура проекта имеет следующий вид:
    logs: папка логов;
    modules: папка модулей проекта(модуль распознавания, модуль ner и др.);
    pipelines: папка пайплайнов;
    project_data: папка файлов, связанных с проектом:
          - папка notebooks содержит в себе jupyter тетрадки, которые используются в ходе разработки.
               - файл run_jupyter_container.txt содержит в себе команду запуска контейнера jupyter сервера с тетрадками внутри.
               - доступ через localhost:8888 с токеном или скопировать ссылку из лога контейнера.
          - папка requests_notebook хранит в себе jupyter тетрадку отправки запросов к сервису и примеры.
          - папка traineddata папка моделей распознавания для тессеракта.
          - docker_run_cmd.txt - содержит в себе пример команды запуска проекта в контейнеризированном виде.
          - requirements.txt - информация о python зависимостях проекта.
          - todo.txt - todo список.
    uploaded_data - папка хранения файлов, загруженных на сервер через запросы;
    utils: папка хранения библиотек, связанных с работой веб-сервиса;

    Dockerfile: файл сборки образа под проект;
    settings.py: настройки веб-сервиса;
    web_service.py: главный файл запуска веб-сервиса.

### Структура модуля распознавания:
    temp: папка временных файлов модуля;
    settings: настройки модуля.
  
### Структура модулей NER(аналогично модулю распознавания):
    settings: настройки модуля.
