from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chatbot</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f4f9; display: flex; flex-direction: column; align-items: center; padding: 20px; }
            #chatbox { width: 600px; height: 400px; border: 1px solid #ccc; border-radius: 12px; padding: 10px; overflow-y: auto; background: #fff; display: flex; flex-direction: column; }
            .msg { margin: 8px 0; padding: 8px 12px; border-radius: 12px; max-width: 80%; }
            .user { background: #0078ff; color: #fff; align-self: flex-end; }
            .bot { background: #eee; color: #333; align-self: flex-start; }
            #inputbox { margin-top: 10px; width: 600px; display: flex; }
            input { flex: 1; padding: 10px; border-radius: 8px; border: 1px solid #ccc; }
            button { padding: 10px 20px; margin-left: 5px; border-radius: 8px; background: #0078ff; color: #fff; border: none; cursor: pointer; }
            button:hover { background: #005fcc; }
        </style>
    </head>
    <body>
        <h2>💬 Mon Chatbot Touristique</h2>
        <div id="chatbox"></div>
        <div id="inputbox">
            <input id="userInput" type="text" placeholder="Écris ton message..." />
            <button onclick="sendMessage()">Envoyer</button>
        </div>
        <script>
            async function sendMessage() {
                const input = document.getElementById("userInput");
                const chatbox = document.getElementById("chatbox");
                const message = input.value.trim();
                if (!message) return;

                // Afficher le message utilisateur
                const userMsg = document.createElement("div");
                userMsg.className = "msg user";
                userMsg.textContent = message;
                chatbox.appendChild(userMsg);
                chatbox.scrollTop = chatbox.scrollHeight;

                input.value = "";

                // Envoyer à ton API
                const resp = await fetch("/api/v1/chat", {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json",
                        "x-api-key": "AdxzFiqFQsISvSQ7c2mn4sLxhoFTPh0k"   // 👉 ajoute ta clé ici
                    },
                    body: JSON.stringify({ messages: [{role: "user", content: message}] })
                });
                const data = await resp.json();

                // Afficher la réponse du bot
                const botMsg = document.createElement("div");
                botMsg.className = "msg bot";
                botMsg.textContent = data.reply;
                chatbox.appendChild(botMsg);
                chatbox.scrollTop = chatbox.scrollHeight;
            }
        </script>
    </body>
    </html>
    """