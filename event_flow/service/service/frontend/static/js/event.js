document.addEventListener('DOMContentLoaded', async () => {
    const eventId = window.location.pathname.split('/').pop();
    const token = localStorage.getItem("access_token");

    let currentUser = null;
    let eventData = null;

    try {

        const userResp = await fetch('http://10.14.9.50:1337/api/user', { headers: {"Authorization": `Bearer ${token}`} });
        if (userResp.status == 401) { window.location.href = '/login';}
        if (userResp.ok) {
            currentUser = await userResp.json(); 
        }


        const eventResp = await fetch(`http://10.14.9.50:1337/api/event/${eventId}`, { headers: {"Authorization": `Bearer ${token}`} });
        if (eventResp.status == 401) { window.location.href = '/login';}
        if (!eventResp.ok) throw new Error('Failed to fetch event');
        eventData = await eventResp.json();

        populateEvent(eventData);
        applyPermissions();

    } catch (err) {
        console.error('Error loading data:', err);
    }

    function populateEvent(event) {
        const titleH1 = document.querySelector('.event-title .title-h1');
        if (titleH1) titleH1.textContent = event.title;

        const statusInput = document.getElementById('status-input');
        if (statusInput) statusInput.value = event.status;

        const dateInput = document.getElementById('date-input');
        if (dateInput) dateInput.value = event.date;

        const timeInput = document.getElementById('time-input');
        if (timeInput) timeInput.value = event.time;

        const addressInput = document.getElementById('address-input');
        if (addressInput) addressInput.value = event.location_address;

        const ownerP = document.getElementById('owner-username');
        if (ownerP) ownerP.textContent = event.owner_username;

        const descTextarea = document.getElementById('description-textarea');
        if (descTextarea) descTextarea.value = event.description;

    }

    function applyPermissions() {
        const isOwner = currentUser && currentUser.id === eventData.owner_id;
        const isAdmin = currentUser && currentUser.role === "admin";
        const isOrganizer = currentUser && eventData.organizers.includes(currentUser.username);
        
        const saveBtn = document.getElementById('save-btn');
        const taskForm = document.querySelector('.task-form');
        const historyPanel = document.querySelector('.event-panel-wrapper-3');
        const tasksSection = document.querySelector('.event-panel-wrapper-2');
        const joinBtn = document.getElementById('join-btn')
        
        if (saveBtn) saveBtn.style.display = (isOwner) ? 'flex' : 'none';
        if (taskForm) taskForm.style.display = (isOwner || isOrganizer ) ? 'flex' : 'none';
        if (historyPanel) historyPanel.style.display = (isOwner) ? 'flex' : 'none';
        if (tasksSection) tasksSection.style.display = (isOwner || isOrganizer || isAdmin) ? 'flex' : 'none';
        if (joinBtn) joinBtn.style.display = (isOwner || isOrganizer || isAdmin) ? 'none' : 'flex';
        
        if (isOwner || isOrganizer || isAdmin) {
            loadTasks();
            loadHistory()
        }
    
        if (!isOwner) {
            document.getElementById('status-input').disabled = true;
            document.getElementById('date-input').disabled = true;
            document.getElementById('time-input').disabled = true;
            document.getElementById('address-input').disabled = true;
            document.getElementById('description-textarea').disabled = true;
            
        }
    }

    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            const status = document.getElementById('status-input').value;
            const date = document.getElementById('date-input').value;
            const time = document.getElementById('time-input').value;
            const address = document.getElementById('address-input').value;
            const description = document.getElementById('description-textarea').value;


            fetch(`http://10.14.9.50:1337/api/event/${eventId}/update`, { method: "POST", headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` }, body: JSON.stringify(
                { 
                    status: status, 
                    date: date,
                    time: time,
                    location_address: address,
                    description: description 
                }) 
            
            }) .then(response => {
                if (response.status == 401) { window.location.href = '/login';}
                if (response.ok){openModal('Changed successfully!');loadHistory();return;} 
                if (!response.ok){ throw new Error("Failed to update profile"); return response.json(); }
            }).catch(err => 
                console.error("Error:", err));
        });
    }


    const joinBtn = document.getElementById('join-btn');
    if (joinBtn) joinBtn.addEventListener('click', openAddEventModal);


    const addTaskBtn = document.querySelector('.add-task-btn');
    if (addTaskBtn) {
        addTaskBtn.addEventListener('click', () => {
            const taskForm = document.querySelector('.task-form');
            const taskName = taskForm.querySelector('input[type="text"]').value;
            const priority = taskForm.querySelector('select').value.toLowerCase();
            const assignedTo = taskForm.querySelectorAll('input[type="text"]')[1].value;
            const deadline = taskForm.querySelector('input[type="date"]').value;

            if (!taskName || !priority || !assignedTo || !deadline) {
                openModal("Error! Some values are empty!")
                return;
            }
            const token = localStorage.getItem("access_token");
            fetch(`http://10.14.9.50:1337/api/event/${eventId}/task/add`, { method: "POST", headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` }, body: JSON.stringify({ 
                    task_name: taskName, 
                    priority: priority, 
                    assigned_to: assignedTo, 
                    deadline: deadline  
                }) 
            }) .then(response => {
                taskName.value = '';
                priority.value = 'Low';
                assignedTo.value = '';
                deadline.value = ''
                if (response.status == 401) { window.location.href = '/login';}
                if (response.ok) {loadTasks(); loadHistory(); return;}
                if (!response.ok) throw new Error("Failed to create event"); return; 
            }) .catch(err => 
                console.error("Error:", err));       
        

        });


    }

    const tasksContainer = document.querySelector('.tasks-container');

    if (tasksContainer) {
        tasksContainer.addEventListener('change', async (e) => {
            if (!e.target.classList.contains('task-checkbox')) return;
    
            const taskCard = e.target.closest('.task-card');
            const taskMate = taskCard.querySelector('.task-meta');
            const taskIdStrong = taskMate.querySelector('#task_id'); 
            const taskId = taskIdStrong.textContent.trim(); 
            
            const newState = e.target.checked;
        

            taskCard.classList.toggle('completed', newState);
            const token = localStorage.getItem("access_token");
            
            try {
                await fetch(`http://10.14.9.50:1337/api/task/${taskId}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
                    body: JSON.stringify({ completed: newState })
                }) .then(response => {
                    if (response.status == 401) { window.location.href = '/login';}
                    if (response.ok) {loadTasks(); loadHistory(); return;}
                    if (!response.ok) throw new Error("Failed to create event"); return; 
                }) .catch(err => 
                    console.error("Error:", err));
    
            } catch (err) {
                console.log("Ошибка при обновлении задачи", err);
            }
        });
    }
});

async function loadTasks() {
    try {
        const eventId = window.location.pathname.split('/').pop();
        const token = localStorage.getItem("access_token");

        const resp = await fetch(`http://10.14.9.50:1337/api/event/${eventId}/tasks`, { headers: {"Authorization": `Bearer ${token}`} });
        if (!resp.ok) throw new Error('Failed to load tasks');

        const tasks = await resp.json();

        const tasksContainer = document.querySelector('.tasks-container');
        tasksContainer.innerHTML = '';

        tasks.forEach(task => {
            const card = document.createElement('div');
            card.classList.add('task-card');
            if (task.completed) card.classList.add('completed');

            const header = document.createElement('div');
            header.classList.add('task-header');

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.classList.add('task-checkbox');
            checkbox.checked = task.completed;

            const text = document.createElement('span');
            text.classList.add('task-text');
            text.textContent = task.text;

            const pr = document.createElement('span');
            pr.classList.add('task-priority', task.priority.toLowerCase());
            pr.textContent = task.priority;



            header.appendChild(checkbox);
            header.appendChild(text);
            header.appendChild(pr);


            const meta = document.createElement('div');
            meta.classList.add('task-meta');


            const assignedSpan = document.createElement('span');
            assignedSpan.textContent = "Assigned to: ";

            const assignedStrong = document.createElement('strong');
            assignedStrong.textContent = task.assigned_to;
            assignedSpan.appendChild(assignedStrong);


            const deadlineSpan = document.createElement('span');
            deadlineSpan.textContent = "Deadline: ";

            const deadlineStrong = document.createElement('strong');
            deadlineStrong.textContent = task.deadline;
            deadlineSpan.appendChild(deadlineStrong);     


            const task_id = document.createElement('span');
            task_id.textContent = "ID: ";

            const task_id_strong = document.createElement('strong');
            task_id_strong.textContent = task.id;
            task_id_strong.id = 'task_id'
            task_id.appendChild(task_id_strong);     

                        

            meta.appendChild(assignedSpan);
            meta.appendChild(deadlineStrong);
            meta.appendChild(task_id)
            card.appendChild(header);
            card.appendChild(meta);

            tasksContainer.appendChild(card);
        });

    } catch (err) {
        console.error('Error loading tasks:', err);
    }
}

async function loadHistory() {
    try {
        const eventId = window.location.pathname.split('/').pop();
        const token = localStorage.getItem("access_token");

        const resp = await fetch(`http://10.14.9.50:1337/api/event/${eventId}/history`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!resp.ok) {
            throw new Error("Failed to load history");
        }

        const historyList = await resp.json();
        const historyContainer = document.querySelector('.history-container');
        historyContainer.innerHTML = "";

        historyList.forEach(entry => {
            const card = document.createElement('div');
            card.classList.add('history-card');

            const top = document.createElement('div');
            top.classList.add('history-top');

            const action = document.createElement('div');
            action.classList.add('history-action');
            action.textContent = entry.action;

            const user = document.createElement('div');
            user.classList.add('history-user');
            user.textContent = `User: ${entry.user_name}`;

            top.appendChild(action);
            top.appendChild(user);

            const bottom = document.createElement('div');
            bottom.classList.add('history-bottom');

            const time = document.createElement('span');
            time.classList.add('history-time');
            time.innerHTML = `Time: <strong>${entry.timestamp}</strong>`;

            const id = document.createElement('span');
            id.classList.add('history-id');
            id.innerHTML = `Event ID: <strong>${entry.event_id}</strong>`;

            bottom.appendChild(time);
            bottom.appendChild(id);

            card.appendChild(top);
            card.appendChild(bottom);

            historyContainer.appendChild(card);
        });

    } catch (err) {
        console.error("Error loading history:", err);
    }
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
    title.textContent = "Enter a Join Inivecode";
    modalWindow.appendChild(title);

    const event_name = document.createElement("input");
    event_name.placeholder = "Event invitecode...";
    event_name.id = 'invitecode'
    modalWindow.appendChild(event_name);



    const submitBtn = document.createElement("button");
    submitBtn.textContent = "Submit";
    submitBtn.className = "modal-action-btn create-btn";

    submitBtn.addEventListener("click", () => {
        const invitecode = document.getElementById('invitecode').value.trim()
        const eventId = window.location.pathname.split('/').pop();
        
        const token = localStorage.getItem("access_token");
        
        if (!invitecode) {
            openModal('Error! Invitecode is empty');
            return;
        }
        
        fetch(`http://10.14.9.50:1337/api/event/${eventId}/join`, { method: "POST",
            headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` }, 
            body: JSON.stringify({
            invitecode: invitecode, 
        }) 
        
        }) .then(response => { 
            if (response.status == 401) { window.location.href = '/login';}
            if (response.status == 409) { openModal('Error! Wrong invitecode!');}
            if (response.ok){
                location.reload();
            }
            if (!response.ok) throw new Error("Failed to create event"); return response.json(); 
        }) .catch(err => 
            console.error("Error:", err));
        modal.style.display = "none"; 
    });
    
    modalWindow.appendChild(submitBtn);
    
    modal.appendChild(modalWindow);
    
    modal.style.display = "flex";

}


function openModal(message) {
    const modal = document.getElementById("mini-modal");
    modal.textContent = message;

    modal.classList.add("show");

    setTimeout(() => {
        modal.classList.remove("show");
    }, 3000); 
}
