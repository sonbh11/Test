// DOM Elements
const chatBox = document.getElementById("chat-box");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");

// Send message to API and update UI
sendBtn.addEventListener("click", async () => {
  const userMessage = chatInput.value.trim();

  if (!userMessage) {
    alert("Please enter a message.");
    return;
  }

  // Display user's message
  addMessageToChat("user", userMessage);

  // Clear input
  chatInput.value = "";

  try {
    // Send message to Flask API
    const response = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: userMessage }),
    });

    const data = await response.json();

    // Display AI's response
    addMessageToChat("ai", data.response);
  } catch (error) {
    console.error("Error:", error);
    addMessageToChat("ai", "Sorry, something went wrong. Please try again.");
  }
});

// Function to add a message to the chat box
function addMessageToChat(sender, message) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", sender === "user" ? "user-message" : "ai-message");
  messageDiv.textContent = message;
  chatBox.appendChild(messageDiv);

  // Scroll to the bottom
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Add "Enter" key support for sending messages
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    sendBtn.click();
  }
});
