async function logout() {
    const token = localStorage.getItem("access_token");
    try {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
    
    } catch (err) {
        console.error("Error:", err);

    }
}


document.querySelector(".logout").addEventListener("click", function(event) {
    event.preventDefault(); 
    logout();               
});