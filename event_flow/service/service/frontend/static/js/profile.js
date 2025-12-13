document.addEventListener("DOMContentLoaded", () => {
    loadUser();
    setupEditProfileButton();
});

const token = localStorage.getItem("access_token");


async function loadUser() {
    try {
        const res = await fetch(`http://${window.location.hostname}:1337/api/user`,  { headers: {"Authorization": `Bearer ${token}`} });
        if (res.status == 401) { window.location.href = '/login';}
        if (!res.ok) throw new Error("Cannot load user");

        const user = await res.json();

        renderUser(user);
    } catch (err) {
        console.error("Error fetching user:", err);
    }
}

function renderUser(user) {
    const avatar = document.getElementById("user-avatar");
    const username = document.getElementById("user-username");
    const first = document.getElementById("user-first");
    const second = document.getElementById("user-second");
    const email = document.getElementById("user-email");
    const role = document.getElementById("user-role");

    avatar.src = user.avatar || "/static/images/avatars/11.gif";
    username.textContent = user.username || "Username";
    first.textContent = "First Name: " + (user.first_name || "");
    second.textContent = "Second Name: " + (user.second_name || "");
    email.textContent = "Email: " + (user.email || "");
    role.textContent = "Role: " + (user.role || "user");
}


function setupEditProfileButton() {
    const btn = document.getElementById("edit-profile-btn");
    btn.addEventListener("click", () => openAddEventModal());
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
    title.textContent = "Edit profile";
    modalWindow.appendChild(title);
    

    const firstName = document.createElement("input");
    firstName.placeholder = "Enter First Name...";
    firstName.id = 'first_name'
    modalWindow.appendChild(firstName);

    const secondName = document.createElement("input");
    secondName.placeholder = "Enter Second Name...";
    secondName.id = 'second_name'
    modalWindow.appendChild(secondName);

    const email = document.createElement("input");
    email.type = 'email'
    email.placeholder = "Enter Email";
    email.id = "email"
    modalWindow.appendChild(email);



    const submitBtn = document.createElement("button");
    submitBtn.textContent = "Submit";
    submitBtn.className = "modal-action-btn create-btn";

    submitBtn.addEventListener("click", () => {
        const firstName = document.getElementById('first_name').value.trim()
        const secondName = document.getElementById('second_name').value.trim()
        const email = document.getElementById('email').value.trim()


        if (!firstName && !secondName && !email) {
            openModal("Please enter at least one value!");
            return;
        }


        fetch(`http://${window.location.hostname}:1337/api/user/update`, { method: "POST",headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` }, body: JSON.stringify(
            { 
                first_name: firstName, 
                second_name: secondName, 
                email: email
            }) 
        
        }) .then(response => { 
            if (response.status == 401) { window.location.href = '/login';}
            if (response.ok) {loadUser(); openModal('Successfully updated');return;}
            if (response.status == 409) {
                openModal('Username already exist');
                return;
            }
            if (!response.ok){ throw new Error("Failed to update profile"); return response.json(); }

            
        }).catch(err => 
            openModal(`Error: ${err}`));

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
    }, 3000); // скрыть через 3 сек
}
