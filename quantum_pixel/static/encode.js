//cSpell:ignore fastapi
(function () {
    // switching tabs functioning.
    const headers = document.getElementById('tabs-headers');
    const panels = document.getElementById('tabs-panels');
    if (headers && panels) {
        headers.addEventListener('click', (e) => {
            const btn = e.target.closest('.tab-btn');
            if (!btn) return;
            const target = btn.dataset.target;
            headers.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            panels.querySelectorAll('.tab-panel').forEach(p => p.style.display = 'none');
            btn.classList.add('active');
            const panel = document.getElementById(target);
            if (panel) panel.style.display = '';
        });
    }

    // Functions within the tabs section.
    const forms = document.getElementsByClassName('panel-controls');    
    Array.from(forms).forEach(function(form){
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fd = new FormData(form);
            const selected = document.querySelector('#tabs-headers .tab-btn.active').dataset.target;
            fd.append('selected', selected);

            const result = document.querySelector(`#${selected} #result`);
            result.style.display = "";
            result.textContent = 'Loading, please wait patiently.';

            try {
                const r = await fetch(location.pathname, {
                    method: 'POST',
                    body: fd
                });

                const reader = r.body.getReader();
                const decoder = new TextDecoder();
                let buffer = "";

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) {
                        if (buffer.startsWith('{"result":') || buffer.startsWith('{"error":')) {
                            const json = JSON.parse(buffer);

                            const error = document.getElementById("error");
                            if (json.error) {
                                error.innerHTML = json.error;
                            } else {
                                error.style.display = "none";
                            } 

                            if (json.result) {
                                result.innerHTML = json.result;
                            }
                        }
                        break;
                    };

                    buffer += decoder.decode(value, { stream: true });

                    if (buffer.startsWith('{"result":') || buffer.startsWith('{"error":')) {
                        continue; // reserve pure json style.
                    }

                    const lines = buffer.split("\n");
                    buffer = lines.pop();

                    for (const line of lines) {
                        result.textContent = `Progress: ${line}%`;
                    }
                }

            } catch (err) {
                console.error(err);
            }
        });
    })

    // remove file when user left.
    window.addEventListener('beforeunload', () => {
        fetch(`/remove/${location.pathname.split("/").pop()}`, {
            method: 'POST',
            keepalive: true
        });
    });
})();
