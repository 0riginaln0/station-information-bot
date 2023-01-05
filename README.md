# station-information-bot
# Курсовая работа по Конструированию ПО
1. Стриковский С. С.
2. Чирков Н. П.
3. Анастасиев А. С.
## Постановка задачи
Наш проект решает проблему удобства и скорости поиска информации о маршрутах проходящих через избранные остановки.
Телеграм бот, который показывает время и маршрут транспорта по выбранным остановкам. Пользователь копирует ссылку на остановку из Яндекс карт и таким образом может просматривать всю информацию об остановке через бота.
## Описание
1. Пользователь заходит в чат к боту и инициализирует сессию
2. Бот отправляет пользователю приветственное сообщение
3. Пользователь выполняет одно из следующих действий:
   - Пользователь просматривает список своих остановок
     - По выбранной остановке выдаётся список транспорта
   - Пользователь удаляет одну из своих остановок
   - Пользователь открывает туториал
   - Пользователь добавляет остановку
     - Пользователь отпраляет ссылку на остановку
     - Пользователь называет остановку

![block diagram](https://cdn.discordapp.com/attachments/1060524253927194634/1060536382906441738/NRiVJ6pnjbgAAAABJRU5ErkJggg.png)
## Разработка архитектуры и детальное проектировани
System context diagram:
![image](https://cdn.discordapp.com/attachments/1060524253927194634/1060527618191020103/image.png)

Container diagram:
![image](https://cdn.discordapp.com/attachments/1060524253927194634/1060537530442850354/image.png)
## Используемые технологии
Основа приложения строится на Python и соответсвующей библиотеке Telegram Bot API.
Для парсинга и работы с HTML файлами используем библиотеки [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) и [Selenium](https://www.selenium.dev).
