# 1. Predictable Generating Invitecode

## Описание:

> Уязвимость позволяет присоедениться к любому мероприятию из за предсказуемой генерации инвайткода.


Уязвимость находится в файле `service/backend/utils/utils.py`:
```python
def make_invitecode(username, title):
    return hashlib.sha256(f"{str(username)}:{title}".encode('utf-8')).hexdigest()
```

## Суть:
- При создании мероприятия генерируется инвайткод не случайно, а из хэша имени пользователя и названия мероприятия;

## Итог:
- Каждый авторизованный пользователь может присоединться к любому мероприятию в роли организатора и просматривать все существующие задачи.

[Эксплойт (predictable_invitecode.py)](./predictable_invitecode.py)

# 2. HTTP Parameter Pollution

## Описание:

> Уязвимость заключается в неправильной обработке параметров приходящих от пользователя без должной проверки, что позволяет перезаписать роль пользователя на платформе

```python
set_clause = ", ".join([f"{key} = %s" for key in params.keys()])
sql = f"UPDATE users SET {set_clause} WHERE id = %s"
values = list(params.values()) + [user_id]
```

## Эксплуатация

- Можно отправить пост запрос на /api/user/update для изменения роли юзера

```json
{
    'role': 'admin'
}
```

[Эксплойт (role_changing.py)](./role_changing.py)

