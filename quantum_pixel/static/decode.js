(async function () {
    const form = document.getElementsByClassName('panel-controls')[0];    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const result = document.getElementById("result");
        result.style.display = "";
        result.innerHTML =  "Loading, please wait patiently. (If the wait time is too long, it is recommended to use the local version.)";

        const fd = new FormData(form);
        
        try {
            const r = await fetch(location.pathname, {
                method: 'POST',
                body: fd
            });
            const json = await r.json();
            
            if (json.error) {
                const error = document.getElementById("error");
                error.style.display = "";
                error.innerHTML = json.error;
            } else {
                error.style.display = "none";
            }

            if (json.result) {
                result.innerHTML = json.result;
            }
        } catch (err) {
            console.error(err);
        }
    });

    // remove file when user left.
    window.addEventListener('beforeunload', () => {
        fetch(`/remove/${location.pathname.split("/").pop()}`, {
            method: 'POST',
            keepalive: true
        });
    });
})();