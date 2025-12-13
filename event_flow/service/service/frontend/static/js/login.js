document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");

    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault(); 

        const username = document.getElementById("username").value
        const password = document.getElementById("password").value


        try {
            const response = await fetch(`http://${window.location.hostname}:1337/api/login`, {
                method: "POST",
                credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username: username, password: password })
            });
        
            if (response.ok) {
                const responseData = await response.json();
                localStorage.setItem("access_token", responseData.token);
                window.location.href = "/dashboard"; 
            } else {
                const data = await response.json();   
                openModal(data.message);      
            }
        } catch (err) {
            console.error("Error:", err);
        }
    });
});

function openModal(message) {
    const modal = document.getElementById("mini-modal");
    modal.textContent = message;

    modal.classList.add("show");

    setTimeout(() => {
        modal.classList.remove("show");
    }, 3000);
}
