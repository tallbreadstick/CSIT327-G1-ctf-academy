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
        if (e.target.closest(".win-btn")) return;

        dragging = true;
        offsetX = e.clientX - win.offsetLeft;
        offsetY = e.clientY - win.offsetTop;

        e.preventDefault();
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
   POWER MENU FIX
   ======================================================= */
document.addEventListener("DOMContentLoaded", () => {
    const powerBtn = document.getElementById("power-btn");
    const powerDropdown = document.getElementById("power-dropdown");

    if (!powerBtn || !powerDropdown) return; // Safety check

    // Toggle dropdown visibility
    powerBtn.addEventListener("click", e => {
        e.stopPropagation(); // prevent document click from closing it immediately
        powerDropdown.classList.toggle("dropdown-hidden");

        // Get button position
        const rect = powerBtn.getBoundingClientRect();

        // Position dropdown above the button (taskbar is at bottom)
        const dropdownHeight = powerDropdown.offsetHeight;
        const margin = 6;

        // The button's bottom coordinate
        const btnBottom = rect.bottom;

        // Since taskbar is at bottom, calculate from viewport height
        powerDropdown.style.top = `${window.innerHeight - rect.bottom - dropdownHeight - margin}px`;

        // Align left with button
        powerDropdown.style.left = `${rect.left}px`;
    });

    // Close dropdown if click outside
    document.addEventListener("click", e => {
        if (!powerDropdown.contains(e.target) && !powerBtn.contains(e.target)) {
            powerDropdown.classList.add("dropdown-hidden");
        }
    });

    // Button actions
    powerDropdown.querySelectorAll("button").forEach(btn => {
        btn.addEventListener("click", () => {
            const url = btn.getAttribute("data-url");
            const action = btn.getAttribute("data-action");

            if (url) {
                window.location.href = url; // navigate to URL
            } else if (action === "restart") {
                alert("Restart feature to be implemented");
            }

            powerDropdown.classList.add("dropdown-hidden");
        });
    });
});

/* =======================================================
     PROGRESS SAVE (resume + unsaved warning support)
     ======================================================= */
document.addEventListener("DOMContentLoaded", () => {
    const area = document.querySelector('.desktop-area');
    if(!area) return;
    const readonly = area.getAttribute('data-readonly') === 'true';
    const saveUrl = area.getAttribute('data-save-url');
    if(readonly || !saveUrl) return;

    function getCookie(name){
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if(parts.length === 2) return parts.pop().split(';').shift();
    }

    function collectState(){
        // Minimal example: capture text editor contents if present
        const editor = document.querySelector('#welcome-editor textarea');
        const text = editor ? editor.value : null;
        return { text };
    }

    async function saveOnce(){
        try{
            const body = JSON.stringify({ last_state: collectState() });
            await fetch(saveUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body
            });
        }catch(e){
            // ignore; server will keep last_saved_ok=false and UI will show warning
        }
    }

    // Save shortly after load and periodically
    setTimeout(saveOnce, 1500);
    const interval = setInterval(saveOnce, 15000);
    window.addEventListener('beforeunload', () => {
        clearInterval(interval);
        // Try to save one last time (best effort)
        if(navigator.sendBeacon){
            const data = new Blob([JSON.stringify({ last_state: collectState() })], {type:'application/json'});
            navigator.sendBeacon(saveUrl, data);
        }else{
            saveOnce();
        }
    });
});
