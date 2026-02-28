(async function () {
    const form = document.getElementsByClassName('upload-form')[0];    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const result = document.getElementById("result");
        result.style.display = "";
        result.innerHTML =  "Loading, please wait patiently. (If the wait time is too long, it is recommended to use the local version.)";

        const fd = new FormData(form, e.submitter);

        try {
            const r = await fetch(location.pathname, {
                method: 'POST',
                body: fd
            });
            const json = await r.json();
            
            const error = document.getElementById("error");
            if (json.error) {
                result.style.display = "none";
                error.style.display = "";
                error.innerHTML = json.error;
            } else {
                error.style.display = "none";
            }

            if (json.redirect) {
                window.location.href = json.redirect;
            }

        } catch (err) {
            console.error(err);
        }
    });
})();