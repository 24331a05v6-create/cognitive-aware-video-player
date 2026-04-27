function sendMessage() {
    const input = document.getElementById("userInput");
    const chatBox = document.getElementById("chatBox");
    const message = input.value.trim();

    if (!message) return;

    // User message
    const userMsg = document.createElement("div");
    userMsg.className = "msg user";
    userMsg.textContent = message;
    chatBox.appendChild(userMsg);

    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // Typing indicator
    const typing = document.createElement("div");
    typing.className = "msg ai typing";
    typing.id = "typingIndicator";
    typing.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;
    chatBox.appendChild(typing);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Send to backend
    fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: message })
    })
    .then(res => res.json())
    .then(data => {
        typing.remove();

        const aiMsg = document.createElement("div");
        aiMsg.className = "msg ai";
        aiMsg.innerHTML = marked.parse(data.response);

        chatBox.appendChild(aiMsg);
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}


function handleKey(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}
