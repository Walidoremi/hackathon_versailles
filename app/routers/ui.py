from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>🤴 Chatbot - Château de Versailles</title>
        <style>
            body {
                font-family: 'Georgia', serif;
                background: linear-gradient(to bottom, #f9f6f1, #e0d4b7);
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
                color: #3e2f1c;
            }
            h2 {
                color: #7a5c2e;
                margin-bottom: 15px;
            }
            #chatbox {
                width: 650px;
                height: 450px;
                border: 2px solid #d1b97f;
                border-radius: 12px;
                padding: 15px;
                overflow-y: auto;
                background: #fffdf7;
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                display: flex;
                flex-direction: column;
            }
            .msg {
                margin: 8px 0;
                padding: 10px 14px;
                border-radius: 12px;
                max-width: 80%;
                line-height: 1.4;
            }
            .user {
                background: #7a5c2e;
                color: #fff;
                align-self: flex-end;
            }
            .bot {
                background: #f5e6c8;
                color: #3e2f1c;
                align-self: flex-start;
                border-left: 4px solid #d1b97f;
                white-space: pre-line;
            }
            #inputbox {
                margin-top: 12px;
                width: 650px;
                display: flex;
            }
            input {
                flex: 1;
                padding: 12px;
                border-radius: 8px;
                border: 1px solid #ccc;
                font-size: 15px;
            }
            button {
                padding: 12px 20px;
                margin-left: 5px;
                border-radius: 8px;
                background: #d1b97f;
                color: #3e2f1c;
                font-weight: bold;
                border: none;
                cursor: pointer;
                transition: background 0.3s;
            }
            button:hover {
                background: #bfa35d;
            }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    </head>
    <body>
        <h2>🤴 Chatbot Touristique - Château de Versailles</h2>
        <div id="chatbox"></div>
        <div id="inputbox">
            <input id="userInput" type="text" placeholder="Écris ta demande (ex: propose-moi un itinéraire pour demain)..." />
            <button type="button" onclick="sendMessage()">Envoyer</button>
        </div>
        <script>
            async function sendMessage() {
                const input = document.getElementById("userInput");
                const chatbox = document.getElementById("chatbox");
                const message = input.value.trim();
                if (!message) return;

                // Message utilisateur
                const userMsg = document.createElement("div");
                userMsg.className = "msg user";
                userMsg.textContent = message;
                chatbox.appendChild(userMsg);
                chatbox.scrollTop = chatbox.scrollHeight;

                input.value = "";

                try {
                    // Appel API multi-agent
                    const resp = await fetch("/api/v1/multi-chat", {
                        method: "POST",
                        headers: { 
                            "Content-Type": "application/json",
                            "x-api-key": "AdxzFiqFQsISvSQ7c2mn4sLxhoFTPh0k"   // 👉 remplace par ta clé 
                        },
                        body: JSON.stringify({ 
                            user_input: message,
                            date: new Date().toISOString().split("T")[0], 
                            weather_csv: "data/weather_forecast.csv",
                            events_csv: "data/versailles_events.csv"
                        })
                    });

                    if (!resp.ok) {
                        throw new Error(await resp.text());
                    }

                    const data = await resp.json();

                    // Réponse structurée
                    const botMsg = document.createElement("div");
                    botMsg.className = "msg bot";

                    let formatted;
                    if (data.mode === "qa" || data.mode === "doc") {
                        formatted = data.answer;
                    } else if (data.mode === "itinerary") {
                        formatted = `
### 🧭 Itinéraire proposé
${data.itinerary}

---

### 🎭 Profil
${data.profiling}

### ⚠️ Contraintes
${data.constraints}
                        `;
                    } else {
                        formatted = data.answer || "⚠️ Je n’ai pas compris la demande.";
                    }

                    botMsg.innerHTML = marked.parse(formatted);
                    chatbox.appendChild(botMsg);
                    chatbox.scrollTop = chatbox.scrollHeight;
                } catch (err) {
                    const botMsg = document.createElement("div");
                    botMsg.className = "msg bot";
                    botMsg.textContent = "⚠️ Erreur API: " + err.message;
                    chatbox.appendChild(botMsg);
                }
            }

            // Envoi avec touche Entrée
            document.getElementById("userInput").addEventListener("keypress", function(e) {
                if (e.key === "Enter") {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """
