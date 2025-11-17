/* =======================================================
   CLOCK
   ======================================================= */
function updateClock() {
    const now = new Date();
    document.getElementById("clock").textContent =
        now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
setInterval(updateClock, 1000);
window.onload = updateClock;

/* =======================================================
   WINDOW OPEN/CLOSE/MAXIMIZE/MINIMIZE
   ======================================================= */
function openWindow(id) {
    const win = document.getElementById(id);
    win.classList.remove("hidden");
}

function closeWindow(id) {
    const win = document.getElementById(id);
    win.classList.add("hidden");
}

function minimizeWindow(id) {
    const win = document.getElementById(id);
    win.style.display = (win.style.display === "none") ? "flex" : "none";
}

function maximizeWindow(id) {
    const win = document.getElementById(id);

    if (!win.dataset.prev) {
        // Store previous position & size
        win.dataset.prev = JSON.stringify({
            left: win.offsetLeft,
            top: win.offsetTop,
            width: win.offsetWidth,
            height: win.offsetHeight
        });

        win.style.left = "0px";
        win.style.top = "0px";
        win.style.width = window.innerWidth + "px";
        win.style.height = (window.innerHeight - 48) + "px"; // 48px for taskbar
    } else {
        // Restore previous position & size
        const prev = JSON.parse(win.dataset.prev);
        win.style.left = prev.left + "px";
        win.style.top = prev.top + "px";
        win.style.width = prev.width + "px";
        win.style.height = prev.height + "px";

        delete win.dataset.prev;
    }
}

/* =======================================================
   DRAG + RESIZE SYSTEM
   ======================================================= */
function makeDraggableAndResizable(winId) {
    const win = document.getElementById(winId);
    const header = win.querySelector(".window-header");
    const resizer = win.querySelector(".resizer");

    let dragging = false;
    let resizing = false;

    let offsetX, offsetY;
    let startW, startH, startX, startY;

    const MIN_W = 260;
    const MIN_H = 140;

    /* DRAG */
    header.addEventListener("mousedown", e => {
        // Ignore clicks on control buttons
        if (e.target.closest(".win-btn")) return;

        dragging = true;
        offsetX = e.clientX - win.offsetLeft;
        offsetY = e.clientY - win.offsetTop;

        e.preventDefault(); // prevent text selection
    });

    /* RESIZE */
    resizer.addEventListener("mousedown", e => {
        resizing = true;
        startW = win.offsetWidth;
        startH = win.offsetHeight;
        startX = e.clientX;
        startY = e.clientY;
        e.stopPropagation();
        e.preventDefault();
    });

    document.addEventListener("mousemove", e => {
        if (dragging) {
            let left = e.clientX - offsetX;
            let top = e.clientY - offsetY;

            left = Math.max(0, Math.min(left, window.innerWidth - win.offsetWidth));
            top = Math.max(0, Math.min(top, window.innerHeight - win.offsetHeight - 48));

            win.style.left = `${left}px`;
            win.style.top = `${top}px`;
        }

        if (resizing) {
            let width = startW + (e.clientX - startX);
            let height = startH + (e.clientY - startY);

            width = Math.max(MIN_W, width);
            height = Math.max(MIN_H, height);

            const rect = win.getBoundingClientRect();
            width = Math.min(width, window.innerWidth - rect.left);
            height = Math.min(height, window.innerHeight - rect.top - 20);

            win.style.width = `${width}px`;
            win.style.height = `${height}px`;
        }
    });

    document.addEventListener("mouseup", () => {
        dragging = false;
        resizing = false;
    });
}

document.addEventListener("DOMContentLoaded", () => {
    // Initialize all c-windows automatically
    document.querySelectorAll(".c-window").forEach(win => {
        makeDraggableAndResizable(win.id);
    });
});

/* =======================================================
   POWER MENU
   ======================================================= */
function togglePowerDropdown() {
    document.getElementById("power-dropdown").classList.toggle("hidden");
}

document.addEventListener("click", e => {
    const dropdown = document.getElementById("power-dropdown");
    const button = document.getElementById("power-btn");

    if (!dropdown.contains(e.target) && !button.contains(e.target)) {
        dropdown.classList.add("hidden");
    }
});
