document.addEventListener("DOMContentLoaded", () => {
    const loading = document.getElementById("loading-screen");
    const fullscreenPrompt = document.getElementById("fullscreen-prompt");
    const loadingExtra = document.getElementById("loading-extra");

    // Animate loading messages
    const extraMessages = [
        "Loading modules...",
        "Fetching challenge data...",
        "Preparing your desktop...",
        "Almost ready..."
    ];
    let msgIndex = 0;
    const msgInterval = setInterval(() => {
        if (msgIndex < extraMessages.length) {
            loadingExtra.textContent = extraMessages[msgIndex];
            msgIndex++;
        } else {
            clearInterval(msgInterval);
        }
    }, 800);

    // 1️⃣ Keep loading screen visible for 4 seconds
    setTimeout(() => {
        // 2️⃣ Fade out loading screen
        if (loading) {
            loading.classList.add("opacity-0", "pointer-events-none");
            setTimeout(() => loading.remove(), 500);
        }

        // 3️⃣ Type editor content after loading fade
        const editor = document.querySelector("#welcome-editor textarea");
        if (editor && editor.textContent) {
            const text = editor.textContent;
            editor.value = "";
            let i = 0;
            const interval = setInterval(() => {
                editor.value += text[i];
                i++;
                if (i >= text.length) clearInterval(interval);
            }, 15);
        }

        // 4️⃣ Show fullscreen prompt AFTER loading screen completely disappears
        setTimeout(() => {
            fullscreenPrompt.classList.remove("opacity-0", "pointer-events-none");
            fullscreenPrompt.classList.add("opacity-100", "pointer-events-auto");
        }, 500); // 0.5s fade buffer

    }, 4000); // 4s loading duration

    // 5️⃣ Fullscreen trigger on click
    fullscreenPrompt.addEventListener("click", () => {
        const el = document.documentElement;
        if (el.requestFullscreen) el.requestFullscreen();
        else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
        else if (el.msRequestFullscreen) el.msRequestFullscreen();

        fullscreenPrompt.classList.add("opacity-0", "pointer-events-none");
        setTimeout(() => fullscreenPrompt.remove(), 500);

        // When the user clicks to continue, after fade-out completes
        document.dispatchEvent(new Event("challenge-start"));
    });
});