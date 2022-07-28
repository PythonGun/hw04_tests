# hw04_tests

### Используется:

[![Python](https://img.shields.io/badge/-Python_3.7.9-464646??style=flat-square&logo=Python)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/-Django-464646??style=flat-square&logo=Django)](https://www.djangoproject.com/)

## Описание
Это учебный проект, выполненный в рамках обучения на Python-разработчика в Яндекс.Практикум. Цель проекта - создание cоциальной сети Yatube для размещения постов с авторизацией, персональными лентами, комментариями и подпиской на авторов. Это промежуточная версия, целью которой было покрытие проекта тестами. 

# Установка
<details><summary>Установка</summary>
 
_На Mac или Linux используем Bash_
_Для Windows PowerShell_

#### Клонируем репозиторий на локальную машину:
```
https://github.com/PythonGun/api_yamdb
git clone git@github.com:PythonGun/git@github.com:PythonGun/hw04_tests.git
```

#### Создаем и активируем виртуальное окружение:
Для Mac или Linux
```
python3 -m venv venv
source venv/bin/activate
```

Для Windows
```
python -m venv venv
source venv/Scripts/activate
```

#### Устанавливаем зависимости:
```
pip install -r requirements.txt
```

#### Запускаем миграции:
```
python manage.py migrate
```

#### Запускаем проект:
```
python manage.py runserver
```
</details>

## Автор
- :white_check_mark: [Баринов Денис](https://github.com/PythonGun)
