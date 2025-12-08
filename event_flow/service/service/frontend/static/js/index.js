document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem("access_token");
    const response = await fetch('http://10.14.9.50:1337/api/auth', { headers: {"Authorization": `Bearer ${token}`} });

    if (token != undefined) {
        const unauth = document.querySelector("#unauth")
        unauth.className = "hidden"

        const auth = document.querySelector("#auth")
        auth.className = "buttons"
    }
})