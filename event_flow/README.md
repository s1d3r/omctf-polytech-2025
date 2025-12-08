# Сервис "EventFlow"

## Что внутри
- `service/` — основной фронт/бэк + docker-compose.
- `checker/` — ForcAD чекер.
- `sploits/` — рабочие эксплойты и описание уязвимостей.

## Кратко про уязвимости
- Предсказуемый инвайткод (`service/service/backend/utils/utils.py:4`): invitecode считается как `sha256(f"{username}:{title}")`, зная владельца и название ивента можно подобрать код и стать организатором любого события. Эксплойт: `sploits/predictable_invitecode.py`.
- Mass assignment роли (`service/service/backend/routes/api.py` + `service/service/backend/database/db.py:47`): `/api/user/update` принимает любые поля и `update_user` строит SQL без вайтлиста — обычный пользователь может сменить себе `role` на `admin` и читать задачи/флаги. Эксплойт: `sploits/role_changing.py`.

## Как поднять локально
1. Перейти в `service/`.
2. Запустить `docker-compose up -d --build`.
3. Эксплойты и детали атак — в `sploits/README.md`.
