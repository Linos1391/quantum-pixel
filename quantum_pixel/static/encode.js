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
                const TIMEOUT = 300_000; // 5 minutes.
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), TIMEOUT);

                const r = await fetch(location.pathname, {
                    method: 'POST',
                    body: fd,
                    signal: controller.signal
                });

                const reader = r.body.getReader();
                const decoder = new TextDecoder();
                let buffer = "";

                let end_timeout = true
                while (true) {
                    const { value, done } = await reader.read();
                    if (done) {
                        if (buffer.startsWith('{"result":') || buffer.startsWith('{"error":')) {
                            const json = JSON.parse(buffer);

                            const error = document.getElementById("error");
                            if (json.error) {
                                
                                error.style.display = "";
                                error.innerHTML = json.error;
                            } else {
                                error.style.display = "none";
                            } 

                            if (json.result) {
                                result.style.display = "";
                                result.innerHTML = json.result;
                            } else {
                                result.style.display = "none";
                            }
                        }
                        break;
                    }
                    else if (end_timeout) {
                        end_timeout = false;
                        clearTimeout(timeoutId);
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
                if (err.name.startsWith("TimeoutError") || err.name.startsWith("AbortError")) {
                    const error = document.getElementById("error");
                    error.style.display = "";
                    error.innerHTML = "TimeoutError: The system has reach timeout of 5 minutes. This might be due to RAM limit exceed, use local system instead.";
                } else {
                    console.error(err);
                }
            }
        });
    })

    // remove file when user left.
    window.addEventListener('beforeunload', () => {
        const error = document.getElementById("error");
        error.style.display = "";
        error.innerHTML = "ExitError: You just exit and got auto cleanup!";

        fetch(`/remove/${location.pathname.split("/").pop()}`, {
            method: 'POST',
            keepalive: true
        });
    });
})();
