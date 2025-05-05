from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
import httpx
from typing import Dict, Any, Optional
import uvicorn

# CHALLENGE: Implementing a simple in-memory chat history storage
# SOLUTION: Use a dictionary to store chat sessions keyed by session IDs

app = FastAPI(title="Web-based Chat Assistant")

# Allow CORS for frontend deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for chat sessions
chat_sessions: Dict[str, list] = {}

# Placeholder for LLM API endpoint and API key
# In production, replace with actual LLM API details
LLM_API_URL = "https://api.litellm.com/v1/generate"
API_KEY = "your_api_key_here"  # Replace with your actual API key

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Serve the main HTML page for the chat UI.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chat Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #chat { border: 1px solid #ccc; padding: 10px; height: 400px; overflow-y: scroll; }
            #user_input { width: 80%; }
            #send_button { width: 15%; }
        </style>
    </head>
    <body>
        <h1>Web-based Chat Assistant</h1>
        <div id="chat"></div>
        <form id="chat_form">
            <input type="text" id="user_input" autocomplete="off" placeholder="Type your message" required />
            <button type="submit" id="send_button">Send</button>
        </form>
        <script>
            const chatDiv = document.getElementById('chat');
            const form = document.getElementById('chat_form');
            const input = document.getElementById('user_input');

            // Generate a simple session ID
            let session_id = localStorage.getItem('session_id');
            if (!session_id) {
                session_id = Math.random().toString(36).substring(2);
                localStorage.setItem('session_id', session_id);
            }

            function appendMessage(sender, message) {
                const msgDiv = document.createElement('div');
                msgDiv.innerHTML = `<b>${sender}:</b> ${message}`;
                chatDiv.appendChild(msgDiv);
                chatDiv.scrollTop = chatDiv.scrollHeight;
            }

            form.onsubmit = async (e) => {
                e.preventDefault();
                const message = input.value;
                appendMessage('User', message);
                input.value = '';

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ session_id, message }),
                    });
                    if (response.ok) {
                        const data = await response.json();
                        appendMessage('Assistant', data.reply);
                    } else {
                        appendMessage('Error', 'Failed to get response.');
                    }
                } catch (err) {
                    appendMessage('Error', 'Network error.');
                }
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """
    Handle chat messages from the frontend.
    """
    try:
        data = await request.json()
        session_id: str = data.get("session_id")
        message: str = data.get("message")
        if not session_id or not message:
            raise HTTPException(status_code=400, detail="Missing session_id or message")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request payload")
    
    # Retrieve chat history for session
    history = chat_sessions.get(session_id, [])
    # Append user's message
    history.append({"role": "user", "content": message})
    
    # Generate LLM response
    try:
        reply = await generate_llm_response(history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM API error: {str(e)}")
    
    # Append assistant's reply to history
    history.append({"role": "assistant", "content": reply})
    chat_sessions[session_id] = history
    
    return JSONResponse(content={"reply": reply})

async def generate_llm_response(history: list) -> str:
    """
    Send the conversation history to the LLM API and get a response.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "messages": history,
        # Additional parameters as required by the LLM API
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(LLM_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        # DETAIL: Extract the generated text from the API response
        reply = data.get("choices", [{}])[0].get("text", "").strip()
        if not reply:
            raise ValueError("Empty response from LLM API")
        return reply

# CHALLENGE: Ensuring the server runs correctly on deployment platforms like Render
# SOLUTION: Use uvicorn.run() in the main block

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)