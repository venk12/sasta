from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

client = OpenAI()
completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "write a haiku about ai"}
    ]
)

with st.chat_message(name = "user", avatar="👩🏾‍🎤"):
    st.write(completion.choices[0].message.content)