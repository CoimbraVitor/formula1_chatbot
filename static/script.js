const input = document.getElementById("input");
const messages = document.getElementById("messages");
const button = document.querySelector("button");

let dark = false;
let isLoading = false;

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

window.onload = () => {
  // Start with dark mode for premium feel if you want, but default is light
  addMessage(
    "Olá! 👋 Que bom ter você por aqui. Sou seu assistente especializado em Fórmula 1!\n\nPodemos conversar sobre a história da categoria, as tecnologias incríveis como o DRS, as estratégias de pit stop ou sobre os grandes pilotos. Por onde gostaria de começar nosso papo?",
    "bot"
  );
};
