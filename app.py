import json
from pathlib import Path
import streamlit as st
from langfuse.decorators import observe
from langfuse.openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

model_pricings = {
    "gpt-5.6": {
        "input_tokens": 5.00 / 1_000_000,
        "output_tokens": 30.00 / 1_000_000,
    },
    "gpt-5.6-terra": {
        "input_tokens": 2.50 / 1_000_000,
        "output_tokens": 15.00 / 1_000_000,
    },
    "gpt-5.6-luna": {
        "input_tokens": 1.00 / 1_000_000,
        "output_tokens": 6.00 / 1_000_000,
    },
    "gpt-5.4-mini": {
        "input_tokens": 0.75 / 1_000_000,
        "output_tokens": 4.50 / 1_000_000,
    },
    "gpt-5.4-nano": {
        "input_tokens": 0.20 / 1_000_000,
        "output_tokens": 1.25 / 1_000_000,
    },
    "gpt-4.1-mini": {
        "input_tokens": 0.40 / 1_000_000,
        "output_tokens": 1.60 / 1_000_000,
    },
}

model_descriptions = {
    "gpt-5.6": "🚀 Najmocniejszy — do złożonych zadań i najwyższej jakości odpowiedzi",
    "gpt-5.6-terra": "⚖️ Balans jakości, szybkości i kosztu",
    "gpt-5.6-luna": "💰 Tańszy i szybszy — do codziennych rozmów",
    "gpt-5.4-mini": "⚡ Szybki i wydajny — dobry kompromis do prostszych zadań",
    "gpt-5.4-nano": "💸 Bardzo tani i szybki — do prostych, powtarzalnych zadań",
    "gpt-4.1-mini": "🧠 Lekki model — dobry do prostych rozmów przy niskim koszcie",
}

models = list(model_pricings.keys())

USD_TO_PLN = 3.97

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Chatbot
@observe()
def chatbot_reply(user_prompt, memory, model):
    # Add system message
    messages = [
        {
            "role": "system",
            "content": st.session_state["chatbot_personality"],
        },
    ]
    # Add memory messages
    for message in memory:
        messages.append({"role": message["role"], "content": message["content"]})
    # Add user message
    messages.append({"role": "user", "content": user_prompt})

    response = openai_client.chat.completions.create(
        model=model,
        messages=messages
    )
    usage = {}
    if response.usage:
        usage = {
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "total_tokens": response.usage.total_tokens,
        }

    return {
        "role": "assistant",
        "content": response.choices[0].message.content,
        "usage": {
            **usage,
            "model": model,
        },
    }

# Conversation history and database
DEFAULT_PERSONALITY = """
Jesteś pomocnikiem, który odpowiada na wszystkie pytania użytkownika.
Odpowiadaj na pytania w sposób zwięzły i zrozumiały.
""".strip()

DB_PATH = Path("db")
DB_CONVERSATIONS_PATH = DB_PATH / "conversations"

def load_conversation_to_state(conversation):
    st.session_state["id"] = conversation["id"]
    st.session_state["name"] = conversation["name"]
    st.session_state["messages"] = conversation["messages"]
    st.session_state["chatbot_personality"] = conversation["chatbot_personality"]
    st.session_state["model"] = conversation.get("model", models[0])

def load_current_conversation():
    if not DB_PATH.exists():
        DB_PATH.mkdir()
        DB_CONVERSATIONS_PATH.mkdir()
        conversation_id = 1
        conversation = {
            "id": conversation_id,
            "name": "Konwersacja 1",
            "chatbot_personality": DEFAULT_PERSONALITY,
            "model": models[0],
            "messages": [],
        }

        # Create conversation
        with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
            f.write(json.dumps(conversation))

        # Set current conversation
        with open(DB_PATH / "current.json", "w") as f:
            f.write(json.dumps({
                "current_conversation_id": conversation_id,
            }))

    else:
        # Get current conversation
        with open(DB_PATH / "current.json", "r") as f:
            data = json.loads(f.read())
            conversation_id = data["current_conversation_id"]

        # Load conversation
        with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
            conversation = json.loads(f.read())

    load_conversation_to_state(conversation)

def save_current_conversation_messages():
    conversation_id = st.session_state["id"]
    new_messages = st.session_state["messages"]

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(json.dumps({
            **conversation,
            "messages": new_messages,
        }))

def save_current_conversation_name():
    conversation_id = st.session_state["id"]
    new_conversation_name = st.session_state["new_conversation_name"]

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(json.dumps({
            **conversation,
            "name": new_conversation_name,
        }))

def save_current_conversation_personality():
    conversation_id = st.session_state["id"]
    new_chatbot_personality = st.session_state["new_chatbot_personality"]

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(json.dumps({
            **conversation,
            "chatbot_personality": new_chatbot_personality,
        }))

def save_current_conversation_model():
    conversation_id = st.session_state["id"]
    new_model = st.session_state["model"]

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())

    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(json.dumps({
            **conversation,
            "model": new_model,
        }))

def create_new_conversation():
    # Find next conversation ID
    conversation_ids = []
    for p in DB_CONVERSATIONS_PATH.glob("*.json"):
        conversation_ids.append(int(p.stem))

    # conversation_ids contains all conversation IDs
    conversation_id = max(conversation_ids) + 1
    personality = DEFAULT_PERSONALITY
    if "chatbot_personality" in st.session_state and st.session_state["chatbot_personality"]:
        personality = st.session_state["chatbot_personality"]

    conversation = {
        "id": conversation_id,
        "name": f"Konwersacja {conversation_id}",
        "chatbot_personality": personality,
        "model": st.session_state["model"],
        "messages": [],
    }

    # Create conversation
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "w") as f:
        f.write(json.dumps(conversation))

    # Set current conversation
    with open(DB_PATH / "current.json", "w") as f:
        f.write(json.dumps({
            "current_conversation_id": conversation_id,
        }))

    load_conversation_to_state(conversation)
    st.rerun()

def switch_conversation(conversation_id):
    with open(DB_CONVERSATIONS_PATH / f"{conversation_id}.json", "r") as f:
        conversation = json.loads(f.read())

    # Set current conversation
    with open(DB_PATH / "current.json", "w") as f:
        f.write(json.dumps({
            "current_conversation_id": conversation_id,
        }))

    load_conversation_to_state(conversation)
    st.rerun()

def list_conversations():
    conversations = []
    for p in DB_CONVERSATIONS_PATH.glob("*.json"):
        with open(p, "r") as f:
            conversation = json.loads(f.read())
            conversations.append({
                "id": conversation["id"],
                "name": conversation["name"],
            })

    return conversations

# Main program
load_current_conversation()

st.title("🧪 ChatLab 🧪")

selected_model = st.selectbox(
    "Model",
    models,
    index=models.index(st.session_state["model"]),
    format_func=lambda model: f"{model} — {model_descriptions[model]}",
)

if selected_model != st.session_state["model"]:
    st.session_state["model"] = selected_model
    save_current_conversation_model()

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("O co chcesz spytać?")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response = chatbot_reply(
            prompt,
            memory=st.session_state["messages"][-10:-1],
            model=selected_model,
        )
        st.markdown(response["content"])

    st.session_state["messages"].append({"role": "assistant", "content": response["content"], "usage": response["usage"]})
    save_current_conversation_messages()

with st.sidebar:
    st.subheader("Aktualna konwersacja")
    total_cost = 0
    for message in st.session_state.get("messages") or []:
        if "usage" in message:
            usage = message["usage"]
            pricing = model_pricings.get(usage.get("model"), model_pricings[selected_model])

            total_cost += usage["prompt_tokens"] * pricing["input_tokens"]
            total_cost += usage["completion_tokens"] * pricing["output_tokens"]

    c0, c1 = st.columns(2)
    with c0:
        st.metric("Koszt rozmowy (USD)", f"${total_cost:.4f}")

    with c1:
        st.metric("Koszt rozmowy (PLN)", f"{total_cost * USD_TO_PLN:.4f}")

    st.session_state["name"] = st.text_input(
        "Nazwa konwersacji",
        value=st.session_state["name"],
        key="new_conversation_name",
        on_change=save_current_conversation_name,
    )
    st.session_state["chatbot_personality"] = st.text_area(
        "Osobowość chatbota",
        max_chars=1000,
        height=200,
        value=st.session_state["chatbot_personality"],
        key="new_chatbot_personality",
        on_change=save_current_conversation_personality,
    )

    st.subheader("Konwersacje")
    if st.button("Nowa konwersacja"):
        create_new_conversation()

    conversations = list_conversations()
    sorted_conversations = sorted(conversations, key=lambda x: x["id"], reverse=True)
    for conversation in sorted_conversations[:5]:
        c0, c1 = st.columns([10, 3])
        with c0:
            st.write(conversation["name"])

        with c1:
            if st.button("załaduj", key=conversation["id"], disabled=conversation["id"] == st.session_state["id"]):
                switch_conversation(conversation["id"])
