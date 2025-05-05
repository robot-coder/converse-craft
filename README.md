# README.md

# Web-Based Chat Assistant

This project is a web-based Chat Assistant that allows users to have continuous conversations with selectable Large Language Models (LLMs). It features a user-friendly front-end UI and a back-end API built with FastAPI, deployed on Render.com. Users can select different LLMs, send messages, and view conversation history seamlessly.

## Features

- Web interface for real-time chat interactions
- Support for multiple LLM backends
- Persistent conversation context
- Easy deployment on Render.com

## Technologies Used

- FastAPI for the backend API
- Uvicorn as the ASGI server
- liteLLM for interacting with LLMs
- Starlette for web components
- httpx for HTTP requests
- python-multipart for form data handling

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/chat-assistant.git
cd chat-assistant
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application locally:

```bash
uvicorn main:app --reload
```

The app will be available at `http://127.0.0.1:8000`.

### Deployment on Render.com

- Push your code to a GitHub repository.
- Create a new web service on Render.
- Connect your repository.
- Set the start command to:

```bash
uvicorn main:app --host=0.0.0.0 --port=10000
```

- Ensure environment variables are set if needed.

## Usage

Open your browser and navigate to the deployed URL. Select your preferred LLM, start chatting, and enjoy continuous conversations.

## Files

- `main.py`: Contains the FastAPI application, API endpoints, and chat logic.
- `requirements.txt`: Lists all dependencies.
- `README.md`: This documentation.

## License

This project is licensed under the MIT License.

---

# main.py

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import liteLLM
import httpx

# DETAIL: Define data models for request and response payloads
class Message(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model_name: Optional[str] = "liteLLM"

# Initialize FastAPI app
app = FastAPI()

# CHALLENGE: Serve static files for frontend UI
# SOLUTION: Mount static directory if needed (placeholder)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize available models
AVAILABLE_MODELS = {
    "liteLLM": liteLLM.LiteLLM,  # Assuming liteLLM provides a class for LLM interaction
    # Add other models here if needed
}

# DETAIL: Function to get LLM instance based on model name
def get_llm_instance(model_name: str):
    model_cls = AVAILABLE_MODELS.get(model_name)
    if not model_cls:
        raise HTTPException(status_code=400, detail=f"Model '{model_name}' not supported.")
    return model_cls()

# API endpoint to handle chat messages
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Handle chat messages and return assistant response.
    """
    try:
        llm = get_llm_instance(request.model_name)
        # Concatenate messages for context
        conversation = "\n".join([f"{msg.role}: {msg.content}" for msg in request.messages])
        # Generate response from LLM
        response_text = llm.chat(conversation)
        return JSONResponse(content={"response": response_text})
    except Exception as e:
        # ERROR HANDLING: Return error details
        return JSONResponse(status_code=500, content={"error": str(e)})

# Optional: Serve a simple frontend page
@app.get("/", response_class=HTMLResponse)
async def read_index():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Chat Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #chat { border: 1px solid #ccc; padding: 10px; height: 400px; overflow-y: scroll; }
            #user_input { width: 80%; }
            #send_btn { width: 15%; }
        </style>
    </head>
    <body>
        <h1>Web-Based Chat Assistant</h1>
        <div>
            <label for="model_select">Select Model:</label>
            <select id="model_select">
                <option value="liteLLM">LiteLLM</option>
                <!-- Add other models here -->
            </select>
        </div>
        <div id="chat"></div>
        <input type="text" id="user_input" placeholder="Type your message..." />
        <button id="send_btn">Send</button>

        <script>
            const chatDiv = document.getElementById('chat');
            const inputBox = document.getElementById('user_input');
            const sendBtn = document.getElementById('send_btn');
            const modelSelect = document.getElementById('model_select');

            let messages = [];

            function appendMessage(role, content) {
                const msgDiv = document.createElement('div');
                msgDiv.innerHTML = `<b>${role}:</b> ${content}`;
                chatDiv.appendChild(msgDiv);
                chatDiv.scrollTop = chatDiv.scrollHeight;
            }

            sendBtn.onclick = async () => {
                const userMessage = inputBox.value;
                if (!userMessage) return;
                appendMessage('user', userMessage);
                messages.push({role: 'user', content: userMessage});
                inputBox.value = '';

                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({messages: messages, model_name: modelSelect.value})
                });
                const data = await response.json();
                if (data.response) {
                    appendMessage('assistant', data.response);
                    messages.push({role: 'assistant', content: data.response});
                } else if (data.error) {
                    appendMessage('error', data.error);
                }
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Run the app if executed directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# requirements.txt

fastapi
uvicorn
liteLLM
python-multipart
starlette
httpx