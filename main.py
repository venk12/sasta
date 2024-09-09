from openai import OpenAI
import streamlit as st
import streamlit.components.v1 as components
from component import map

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("sasta")
st.subheader("find the best grocery deals near you")

# Define the system prompt to guide the bot's personality
system_prompt = {
    "role": "system",
    "content": "You are a helpful and resourceful virtual shopping assistant" + 
                "specializing in finding the best grocery prices and deals from local supermarkets," + 
                "including Albert Heijn, ALDI, Jumbo, Lidl, Dirk. You can receive requests" + 
                "for single items or lists of items and provide a clear table showing price comparisons across these stores." +
                "Add a column called Lowest Price 💸 populate it with the supermarket where you can get the best deal"+
                "Below the table also provide the links to the product pages from store which has the lowest price "+
                "You can also provide detailed information on the best deals and offers. such as Albert Heijn BONUS, Jumbo EXTRA" +
                "Also after the table, provide a map with the best path to visit these stores so that users can easily get to them. " +
                " After giving all the details ask them where they usually get their groceries from." +
                " based on their response, give them the savings from the table (cost of groceries from the supermarket they usually buy from vs lowest price)"+
                " and also the monthly savings (how much they save per month) by multiplying the above number by 4" +
                " Once you give this figure, ask for a call to action to signup using this link: https://form.jotform.com/242401875157356"
                "Your tone is friendly, professional, and efficient, helping users save time and money on their grocery shopping." + 
                "Whenever possible, you offer additional tips for budget-friendly choices and seasonal discounts."
}

# Sidebar input for postal code
with st.sidebar:
    st.header("Your Location")
    postal_code = st.text_input("Enter your postal code", value="")


# Display map interactive
# st.write(components.html(map, height=800))

# Display postal code in the main app for testing (you can remove this later)
st.write(f"Postal Code (You can set it through the sidebar): {postal_code}")

# Initialize session state for the model and messages
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = [system_prompt]  # Add system prompt at the start

# Handle user input and bot responses
if prompt := st.chat_input("What do you want to buy today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
        
    st.session_state.messages.append({"role": "assistant", "content": response})
