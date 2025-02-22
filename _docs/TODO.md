Для версии 1.0.0:
- Починить автобилд см ошибку https://chatgpt.com/c/67b9af40-5838-8008-b99f-7aeaa4fbc94d
- Добавить недостающую информацию
  - Даты
  - Содержания
  - Описание

Для версии 1.0.1:
- Вынести supabaseUrl и supabaseKey в переменные среды (добавить изменения в GitHub autobuild)
- Пример для загрузки изображения с сервера Supabase
    final supabase = Supabase.instance.client;
    final Uint8List file = await Supabase.instance.client.storage.from('primary_sources').download('10018/P18.jpg');
- Загрузить, переименовать и добавить все изображения унциала 51 (продолжить отсюда https://www.loc.gov/resource/amedmonastery.00271051554-ma/?sp=20&st=image)
- Загрузить и добавить все изображения унциала 52
- Найти, загрузить и добавить все изображения папируса 115
- Составить список исходников с плохим качеством которые еще нужно поискать