const input = document.getElementById("input");
const messages = document.getElementById("messages");
const button = document.querySelector("button");

let dark = false;
let isLoading = false;

function addMessage(text, type) {
  const div = document.createElement("div");

  if (type === "user") {
    div.className =
      "self-end bg-blue-500 text-white px-4 py-2 rounded-xl max-w-[75%]";
  } else {
    div.className =
      "self-start bg-green-500 text-white px-4 py-2 rounded-xl max-w-[75%]";
  }

  div.innerText = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function showTyping() {
  const div = document.createElement("div");
  div.id = "typing";
  div.className = "self-start bg-gray-400 text-white px-4 py-2 rounded-xl";
  div.innerText = "Digitando...";
  messages.appendChild(div);
}

function removeTyping() {
  const typing = document.getElementById("typing");
  if (typing) typing.remove();
}

function setLoading(state) {
  isLoading = state;
  input.disabled = state;
  button.disabled = state;

  if (state) {
    button.classList.add("opacity-50", "cursor-not-allowed");
  } else {
    button.classList.remove("opacity-50", "cursor-not-allowed");
  }
}

function sendMessage(textParam = null) {
  if (isLoading) return;

  const text = textParam || input.value;
  if (!text) return;

  addMessage(text, "user");
  setLoading(true);
  showTyping();

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text }),
  })
    .then((res) => res.json())
    .then((data) => {
      removeTyping();
      addMessage(data.response, "bot");
      setLoading(false);
    });

  input.value = "";
}

function quick(option) {
  sendMessage(option.toString());
}

input.addEventListener("keypress", function (e) {
  if (e.key === "Enter") sendMessage();
});

function toggleTheme() {
  const body = document.getElementById("body");
  dark = !dark;

  body.classList.toggle("bg-gray-900", dark);
  body.classList.toggle("bg-white", !dark);
}

window.onload = () => {
  addMessage(
    `Olá! 👋

O que você quer saber?

1 - O que é Fórmula 1?
2 - O que é DRS?
3 - O que é Pit Stop?
4 - Quem é Lewis Hamilton?
5 - Quem é Max Verstappen?`,
    "bot"
  );
};
