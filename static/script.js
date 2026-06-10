const input = document.getElementById("input");
const messages = document.getElementById("messages");

let dark = false;
let isLoading = false;
let dashboardLoaded = false;

function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = `message ${type === "user" ? "message-user" : "message-bot"}`;
  div.innerText = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function showTyping() {
  const div = document.createElement("div");
  div.id = "typing";
  div.innerText = "Calculando telemetria...";
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function removeTyping() {
  const typing = document.getElementById("typing");
  if (typing) typing.remove();
}

function setLoading(state) {
  isLoading = state;
  input.disabled = state;
  const sendBtn = document.querySelector(".send-btn");
  sendBtn.disabled = state;
  sendBtn.style.opacity = state ? "0.5" : "1";
}

function sendMessage(textParam = null) {
  if (isLoading) return;

  const text = textParam !== null ? textParam : input.value;
  if (!text.trim()) return;

  addMessage(text, "user");
  input.value = "";

  setLoading(true);
  showTyping();

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text }),
  })
    .then((res) => res.json())
    .then((data) => {
      const delay = Math.min(2500, 600 + data.response.length * 15);

      setTimeout(() => {
        removeTyping();
        addMessage(data.response, "bot");
        setLoading(false);
      }, delay);
    })
    .catch(() => {
      removeTyping();
      addMessage("Ops, houve uma falha na telemetria. Tente novamente!", "bot");
      setLoading(false);
    });
}

input.addEventListener("keypress", function (e) {
  if (e.key === "Enter") sendMessage();
});

function toggleTheme() {
  const body = document.getElementById("body");
  const btn = document.querySelector(".theme-toggle");
  dark = !dark;

  body.className = dark ? "bg-gray-900" : "bg-white";
  btn.innerText = dark ? "☀️" : "🌙";
}

function switchView(view) {
  const isDashboard = view === "dashboard";
  const chatView = document.getElementById("chat-view");
  const dashboardView = document.getElementById("dashboard-view");
  const chatTab = document.getElementById("chat-tab");
  const dashboardTab = document.getElementById("dashboard-tab");

  chatView.hidden = isDashboard;
  dashboardView.hidden = !isDashboard;
  chatView.classList.toggle("active", !isDashboard);
  dashboardView.classList.toggle("active", isDashboard);
  chatTab.classList.toggle("active", !isDashboard);
  dashboardTab.classList.toggle("active", isDashboard);
  chatTab.setAttribute("aria-selected", String(!isDashboard));
  dashboardTab.setAttribute("aria-selected", String(isDashboard));

  if (isDashboard && !dashboardLoaded) {
    loadDashboard();
  }
}

function createText(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = text;
  return element;
}

function loadDashboard() {
  fetch("/insights")
    .then((res) => res.json())
    .then((data) => {
      renderDashboard(data);
      dashboardLoaded = true;
    })
    .catch(() => {
      document.getElementById("prediction-title").textContent = "Telemetria indisponível";
      document.getElementById("prediction-subtitle").textContent =
        "Não foi possível carregar os dados do dashboard agora.";
    });
}

function renderDashboard(data) {
  const prediction = data.prediction;
  const summary = data.summary;
  const top = prediction.top || [];
  const maxProbability = Math.max(...top.map((item) => item.probability), 1);

  document.getElementById("prediction-title").textContent =
    `${prediction.leader} para ${prediction.year}`;
  document.getElementById("prediction-subtitle").textContent =
    `${prediction.team} lidera a projeção do campeonato de pilotos.`;
  document.getElementById("confidence-pill").textContent =
    `Confiança ${prediction.confidence}`;

  const bars = document.getElementById("prediction-bars");
  bars.replaceChildren();
  top.forEach((item) => {
    const row = document.createElement("div");
    row.className = "bar-row";

    const header = document.createElement("div");
    header.className = "bar-row-header";
    header.appendChild(createText("span", "driver-name", item.driver));
    header.appendChild(createText("span", "probability", `${item.probability}%`));

    const track = document.createElement("div");
    track.className = "bar-track";
    const fill = document.createElement("div");
    fill.className = "bar-fill";
    fill.style.width = `${Math.max(6, (item.probability / maxProbability) * 100)}%`;
    track.appendChild(fill);

    const meta = createText(
      "div",
      "bar-meta",
      `${item.team} • ${item.points} pts • ${item.wins} vitórias • ${item.podiums} pódios`
    );

    row.appendChild(header);
    row.appendChild(track);
    row.appendChild(meta);
    bars.appendChild(row);
  });

  const summaryGrid = document.getElementById("summary-grid");
  summaryGrid.replaceChildren();
  [
    ["Temporada", summary.season],
    ["Etapa", summary.latestRound],
    ["GP recente", summary.latestEvent],
    ["Corridas", summary.races],
    ["Pilotos", summary.drivers],
    ["Equipes", summary.teams],
  ].forEach(([label, value]) => {
    const item = document.createElement("div");
    item.className = "summary-item";
    item.appendChild(createText("span", "", label));
    item.appendChild(createText("strong", "", value));
    summaryGrid.appendChild(item);
  });

  renderDataList("standings-list", data.standings, (item) => ({
    main: `${item.position}. ${item.driver}`,
    detail: `${item.team} • ${item.points} pts`,
  }));

  renderDataList("winners-list", data.recentWinners, (item) => ({
    main: `${item.year} — ${item.event}`,
    detail: `${item.driver} (${item.team})`,
  }));

  renderTeamWins(data.teamWins);
}

function renderDataList(id, rows, format) {
  const list = document.getElementById(id);
  list.replaceChildren();
  rows.forEach((row) => {
    const formatted = format(row);
    const item = document.createElement("div");
    item.className = "data-row";
    item.appendChild(createText("span", "data-main", formatted.main));
    item.appendChild(createText("span", "data-detail", formatted.detail));
    list.appendChild(item);
  });
}

function renderTeamWins(rows) {
  const list = document.getElementById("team-wins-list");
  list.replaceChildren();
  const maxWins = Math.max(...rows.map((item) => item.wins), 1);

  rows.forEach((item) => {
    const row = document.createElement("div");
    row.className = "mini-bar-row";
    row.appendChild(createText("span", "mini-label", item.team));

    const track = document.createElement("div");
    track.className = "mini-track";
    const fill = document.createElement("div");
    fill.className = "mini-fill";
    fill.style.width = `${Math.max(8, (item.wins / maxWins) * 100)}%`;
    track.appendChild(fill);

    row.appendChild(track);
    row.appendChild(createText("strong", "mini-value", item.wins));
    list.appendChild(row);
  });
}

window.onload = () => {
  // Start with dark mode for premium feel if you want, but default is light
  addMessage(
    "Olá! 👋 Que bom ter você por aqui. Sou seu assistente especializado em Fórmula 1!\n\nPodemos conversar sobre a história da categoria, as tecnologias incríveis como o DRS, as estratégias de pit stop ou sobre os grandes pilotos. Por onde gostaria de começar nosso papo?",
    "bot"
  );
};
