import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

models = client.models.list()
available_ids = [m.id for m in models.data]
selected_model = next((m for m in available_ids if "haiku" in m), available_ids[0])
print(f"Seçilen model: {selected_model}\n")

response = client.messages.create(
    model=selected_model,
    max_tokens=300,
    messages=[
        {
            "role": "user",
            "content": "Merhaba Claude, ben Selim. API bağlantım başarıyla kuruldu mu? Tek cümlelik esprili bir yanıt ver."
        }
    ]
)

# ThinkingBlock yerine doğrudan metin (text) bloğunu al
reply = next(block.text for block in response.content if block.type == "text")
print("Gelen Yanıt:", reply)
