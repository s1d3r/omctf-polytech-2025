document.addEventListener("DOMContentLoaded", () => {
    
    loadEvents();
});

const token = localStorage.getItem("access_token");

async function loadEvents() {
    try {
        const response = await fetch(`http://${window.location.hostname}:1337/api/events`, { headers: {"Authorization": `Bearer ${token}`} });
        if (response.status == 401) { window.location.href = '/login';}
        if (!response.ok) throw new Error("Cannot load /api/events");

        const events = await response.json();
        renderEvents(events);

    } catch (err) {
        console.error("Error:", err);
    }
}


function renderEvents(events) {
    const container = document.getElementById("events-container");
    container.innerHTML = "";

    events.forEach(event => {
        const card = createEventCard(event);
        container.appendChild(card);
    });


    const addCard = document.createElement("button");
    addCard.className = "card add-card";
    addCard.type = "button";

    const addContent = document.createElement("div");
    addContent.className = "card-body";

    const plus = document.createElement("h2");
    plus.textContent = "+";
    plus.style.fontSize = "3rem";
    plus.style.textAlign = "center";

    addContent.appendChild(plus);
    addCard.appendChild(addContent);

    addCard.addEventListener("click", openAddEventModal);
    container.appendChild(addCard);
}


function createEventCard(event) {
    const card = document.createElement("a");
    card.className = "card";
    card.href = "/event/" + event.id;

    const body = document.createElement("div");
    body.className = "card-body";

    const title = document.createElement("h4");
    title.textContent = event.title;
    body.appendChild(title);

    const desc = document.createElement("p");
    desc.textContent = event.description;
    body.appendChild(desc);

    const info = document.createElement("p");
    info.textContent = `Date: ${event.date}  Time: ${event.time}`;
    body.appendChild(info);


    const user_info = document.createElement("div")
    user_info.className = 'user'
    

    const owner = document.createElement("h5");
    owner.textContent = `${event.owner_username}`;
    owner.className = 'user'
    body.appendChild(owner);

    body.appendChild(user_info)


    card.appendChild(body);

    return card;
}


function openAddEventModal() {
    const modal = document.getElementById("modal");
    

    modal.innerHTML = "";
    

    const modalWindow = document.createElement("div");
    modalWindow.className = "modal-window";
    

    const closeBtn = document.createElement("button");
    closeBtn.className = "modal-close";
    closeBtn.textContent = "✖";
    closeBtn.addEventListener("click", () => modal.style.display = "none");
    modalWindow.appendChild(closeBtn);
    

    const title = document.createElement("h2");
    title.textContent = "Enter an Event Name";
    modalWindow.appendChild(title);
    

    const event_name = document.createElement("input");
    event_name.placeholder = "Event Name...";
    event_name.id = 'eventName'
    modalWindow.appendChild(event_name);

    const event_date = document.createElement("input");
    event_date.type = 'date'
    event_date.id = "eventDate"
    modalWindow.appendChild(event_date);

    const event_time = document.createElement("input");
    event_time.type = 'time'
    event_time.id = "eventTime"
    modalWindow.appendChild(event_time);
    

    const event_description = document.createElement("textarea");
    event_description.type = 'time'
    event_description.id = "eventDescription"
    modalWindow.appendChild(event_description);

    const submitBtn = document.createElement("button");
    submitBtn.textContent = "Submit";
    submitBtn.className = "modal-action-btn create-btn";

    submitBtn.addEventListener("click", () => {
        const eventName = document.getElementById('eventName').value.trim()
        const eventDate = document.getElementById('eventDate').value.trim()
        const eventTime = document.getElementById('eventTime').value.trim()
        const eventDescription = document.getElementById('eventDescription').value.trim()
        
        
        if (!eventName || !eventDate || !eventTime || !eventDescription) {
            openErrorModalEmptyValue()
            return;
        }
        fetch(`http://${window.location.hostname}:1337/api/event/add`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}` 
            },
            body: JSON.stringify({
                title: eventName,
                date: eventDate,
                time: eventTime,
                description: eventDescription
            })
        })
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/login';
                throw new Error("Не авторизован");
            }
        
            if (!response.ok) {
                modal.style.display = "none";
                throw new Error("Ошибка запроса");
            }

            return response.json();
        })
        .then(data => {

            if (data.href) {
                window.location.href = data.href;
            }
        })
        .catch(error => {
            console.error("Ошибка:", error);
        });
        
        
    });
    
    modalWindow.appendChild(submitBtn);
    
    modal.appendChild(modalWindow);
    

    modal.style.display = "flex";

}
    
function openErrorModalEmptyValue() {
    const modal = document.getElementById("modal");

    modal.innerHTML = "";
    
    const modalWindow = document.createElement("div");
    modalWindow.className = "modal-window";
    

    const closeBtn = document.createElement("button");
    closeBtn.className = "modal-close";
    closeBtn.textContent = "✖";
    closeBtn.addEventListener("click", () => openAddEventModal());
    modalWindow.appendChild(closeBtn);
    

    const title = document.createElement("h2");
    title.textContent = "Error! Enter All Values!";
    title.className = 'error-text'
    modalWindow.appendChild(title);
    


    modal.appendChild(modalWindow);
    
    modal.style.display = "flex";
}