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

initializeDashboard();
