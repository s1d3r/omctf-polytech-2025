document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('particle-canvas');
    const ctx = canvas.getContext('2d');

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const PARTICLE_COUNT = 150;
    let particles = [];

    function randomColor() {
        return Math.random() < 0.5 
            ? 'rgba(8, 70, 135, 0.7)'   
            : 'rgba(177, 13, 201, 0.7)';
    }

    function createParticle() {
        const speed = Math.random() * 1.5 + 0.5;
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        const angle = Math.random() * Math.PI * 2;
        const dx = Math.cos(angle) * speed;
        const dy = Math.sin(angle) * speed;
        const color = randomColor();
        return { x, y, dx, dy, r: Math.random() * 3 + 1, color };
    }

    function initParticles() {
        particles = [];
        for (let i = 0; i < PARTICLE_COUNT; i++) {
            particles.push(createParticle());
        }
    }

    function drawParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.fill();

            p.x += p.dx;
            p.y += p.dy;

            if (p.x < 0 || p.x > canvas.width || p.y < 0 || p.y > canvas.height) {
                Object.assign(p, createParticle());
            }
        });

        requestAnimationFrame(drawParticles);
    }

    initParticles();
    drawParticles();
});
