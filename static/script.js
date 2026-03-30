const input = document.getElementById("input");
const messages = document.getElementById("messages");

function addMessage(text, type) {
  const div = document.createElement("div");

  if (type === "user") {
    div.className = "self-end bg-blue-500 px-4 py-2 rounded-xl max-w-[75%]";
  } else {
    div.className = "self-start bg-green-500 px-4 py-2 rounded-xl max-w-[75%]";
  }

  div.innerText = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function sendMessage() {
  const text = input.value;
  if (!text) return;

  addMessage(text, "user");

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text }),
  })
    .then((res) => res.json())
    .then((data) => {
      addMessage(data.response, "bot");
    });

  input.value = "";
}

input.addEventListener("keypress", function (e) {
  if (e.key === "Enter") sendMessage();
});

// mensagem inicial estilizada
window.onload = () => {
  addMessage(
    `Olá! 👋

O que você quer saber?

1 - O que é Fórmula 1?
2 - O que é DRS?
3 - O que é Pit Stop?
4 - Quem é Lewis Hamilton?
5 - Quem é Max Verstappen?

Digite o número ou a pergunta!`,
    "bot"
  );
};
