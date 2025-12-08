document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("register-form");

    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {
            username: document.getElementById("username").value,
            password: document.getElementById("password").value,
            email: document.getElementById("email").value,
            first_name: document.getElementById("first_name").value,
            second_name: document.getElementById("second_name").value
        };

        try {
            const response = await fetch("http://10.14.9.50:1337/api/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            
            
            if (response.ok) {
                const responseData = await response.json();
                console.log(responseData)
                localStorage.setItem("access_token", responseData.token);
                window.location.href = "/dashboard"; 
            } else {
                const data = await response.json();   
                openModal(data.message);      
            }

        } catch (err) {
            openModal(`Registration error: $(err)`);
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
