# Бот Netology_BD_English_bot 
Это бот для социальной сети Телеграмм, который помогает пользователям
осваивать английский язык.
## Запуск
1. Запустить файл tg_bot.py
2. В телеграмме зайти по ссылке https://t.me/Netology_BD_English_bot и ввести команду /start.
3. Для выхода из программы нажать на клавишу "Завершить обучение".

## Описание работы.
# Datebase.py
В файле datebase.py создаются таблицы БД, заполняются начальными данными в виде 10 общих слов из файла "data_file.json".
Также в файле содержатся функции для выборки и изменения данных.
create_table - создание таблиц;
insert_word - добавление записей в таблицу слов (words);
insert_user - добавление записей в таблицу пользователей (users);
insert_users_words_start - добавление общих 10 слов каждому зарегистрированному пользователю в таблицу соответсвия слов пользователей (user_words);
insert_id_user_id_word - добавление новой записи в таблицу user_words;
check_id_user - проверяет есть ли уже данный пользователь в БД;
select_random_word_for_user - выбирает случаное слово на английском для проверки знаний пользователя;
translate_word - возвращает перевод английского слова на русском;
delete_word - удаляет слово у определенного пользователя из таблицы user_words;
check_word - проверяет есть ли слово в таблице word или в таблице user_words у определенного пользователя;
count_word - подсчитывает количество слов в индивидуальном словаре пользователя.
# tg_bot.py
При команде /start осуществляется проверка пользователя. Если он новый, то его данные заносятся в таблицу users и 
в таблицу user_words заносятся 10 слов из общего словаря.
Пользователю предлагается случайно выбранное слово на английском из его индивидуального словаря.
В случае неправильного ответа бот оповещает об этом пользователя и предлагает ему выбрать другой вариант.
Для перехода к следующему слову неоюходимо выбрать кнопку "Дальше"
Пользователь может удалить то слово из своего индивидуального словаря, которое ему предлагает перевести бот.
Пользоатель также может добавить любое слово в свой индвидуальный словарь. Бот предложит ввести слово на английском.
После этого осуществляется проверка на наличие уже этого слова у пользователя в словаре. Если слово есть в таблице words,
то добавляется для данного пользователя в таблицу user_words. Если же этого слова нет и в общем словаре, то она добавляется
и в таблицу word и в таблицу user_words. Если у пользователя уже есть это слово в индивидуальном словаре, то 
бот оповестит его об этом.
После выполнение действий с добавлением/удалением слов бот предоставляет информацию
о количестве слов в индивидуальном словаре пользователя.
Для завершения работы необходимо нажать клавишу "Завершить обучение"