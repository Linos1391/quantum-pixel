(async function () {
    // remove file when user left.
    window.addEventListener('beforeunload', () => {
        fetch(`/remove/${location.pathname.split("/").pop()}`, {
            method: 'POST',
            keepalive: true
        });
    });

    // get the image filename from the current path, e.g. /decode/<filename>
    const save_path = crypto.randomUUID() + ".png";
    try {
        const r = await fetch(location.pathname, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ save_path })
        });
        const text = await r.text();
        document.documentElement.innerHTML = text
    } catch (err) {
        console.error(err);
    }
})();