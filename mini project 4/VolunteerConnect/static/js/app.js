document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("input,select,textarea").forEach(el => {
    if (!el.classList.contains("form-control")) el.classList.add("form-control");
  });
  if (window.VC_LIVE_URL) {
    const refresh = async () => {
      try {
        const response = await fetch(window.VC_LIVE_URL, {headers: {"X-Requested-With":"XMLHttpRequest"}});
        if (!response.ok) return;
        const data = await response.json();
        const pending = document.getElementById("pending-count");
        if (pending) pending.textContent = data.pending;
      } catch (_) {}
    };
    refresh(); setInterval(refresh, 10000);
  }
});
