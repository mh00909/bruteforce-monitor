async function fetchFailedAttempts() {
    const response = await fetch("/api/failed_attempts");
    const data = await response.json();
    return data.failed_attempts;
}

async function fetchBlockedIps() {
    const response = await fetch("/api/blocked_ips");
    const data = await response.json();
    return data.blocked_ips;
}

function renderLoginAttemptsChart(data) {
    const ctx = document.getElementById("loginAttemptsChart").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: "Liczba prób logowania",
                data: Object.values(data),
                backgroundColor: "rgba(255, 99, 132, 0.6)"
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function renderBlockedIpsList(ips) {
    const list = document.getElementById("blockedIpsList");
    list.innerHTML = "";
    ips.forEach(ip => {
        const li = document.createElement("li");
        li.textContent = ip;
        list.appendChild(li);
    });
}

async function initializeDashboard() {
    const attempts = await fetchFailedAttempts();
    const blockedIps = await fetchBlockedIps();

    renderLoginAttemptsChart(attempts);
    renderBlockedIpsList(blockedIps);
}

async function banIp() {
    const ip = document.getElementById("ipInput").value.trim();
    const status = document.getElementById("banStatus");

    if (!ip) {
        status.textContent = "⚠️ Wprowadź adres IP.";
        return;
    }

    const response = await authorizedFetch("/api/block_ip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip })
    });

    const data = await response.json();

    if (response.ok) {
        status.textContent = `✅ ${data.message}`;
        document.getElementById("ipInput").value = "";
        const blockedIps = await fetchBlockedIps();
        renderBlockedIpsList(blockedIps);
    } else {
        status.textContent = `❌ Błąd: ${data.error}`;
    }
}

async function unblockIp() {
    const ip = document.getElementById("unblockIpInput").value.trim();
    const status = document.getElementById("unblockStatus");

    if (!ip) {
        status.textContent = "⚠️ Wprowadź adres IP.";
        return;
    }

    const response = await authorizedFetch("/api/unblock_ip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip })
    });

    const data = await response.json();

    if (response.ok) {
        status.textContent = `✅ ${data.message}`;
        document.getElementById("unblockIpInput").value = "";
        const blockedIps = await fetchBlockedIps();
        renderBlockedIpsList(blockedIps);
    } else {
        status.textContent = `❌ Błąd: ${data.error}`;
    }
}


async function fetchBlockHistory() {
    const response = await fetch("/api/block_history");
    const data = await response.json();
    return data.history;
}

function renderBlockHistory(history) {
    const tableBody = document.querySelector("#historyTable tbody");
    tableBody.innerHTML = ""; 

    history.forEach(entry => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${entry.ip}</td>
            <td>${entry.action === "blocked" ? "🔒 Zablokowano" : "🔓 Odblokowano"}</td>
            <td>${entry.timestamp}</td>
        `;
        tableBody.appendChild(row);
    });
}

async function initializeDashboard() {
    const token = getToken();
    if (!token) {
        console.log("🔒 Brak tokenu. Zaloguj się.");
        return;
    }

    try {
        const attempts = await fetchFailedAttempts();
        const blockedIps = await fetchBlockedIps();
        const history = await fetchBlockHistory();

        renderLoginAttemptsChart(attempts);
        renderBlockedIpsList(blockedIps);
        renderBlockHistory(history);
    } catch (error) {
        console.error("❌ Błąd podczas inicjalizacji:", error);
    }
}

function downloadHistory() {
    fetch("/api/export_history")
        .then(response => {
            if (!response.ok) {
                alert("❌ Nie udało się pobrać historii.");
                return;
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "block_history.csv";
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        });
}


async function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const status = document.getElementById("loginStatus");

    if (!username || !password) {
        status.textContent = "⚠️ Podaj login i hasło.";
        return;
    }

    const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });

    const data = await response.json();

    if (response.ok) {
        localStorage.setItem("jwtToken", data.token);
        status.textContent = "✅ Zalogowano!";
        document.getElementById("loginSection").style.display = "none";
        document.getElementById("dashboardSection").style.display = "block";
        initializeDashboard();
    } else {
        status.textContent = `❌ ${data.error}`;
    }
}

function getToken() {
    return localStorage.getItem("jwtToken");
}

async function authorizedFetch(url, options = {}) {
    const token = getToken();
    if (!token) throw new Error("Brak tokenu. Zaloguj się.");

    options.headers = {
        ...(options.headers || {}),
        Authorization: `Bearer ${token}`,
    };

    return fetch(url, options);
}



initializeDashboard();
