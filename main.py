from openai import OpenAI
import streamlit as st
import streamlit.components.v1 as components
from component import map
import time
import pandas as pd
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from elevenlabs import play, stream, save

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
eleven_client = ElevenLabs(api_key=st.secrets["ELEVEN_LABS_KEY"])

# Load the CSV file
df_prices = pd.read_csv("sample_prices.csv")

st.title("sasta")
st.subheader("find the best grocery deals near you")

# Define the system prompt to guide the bot's personality
system_prompt = {
    "role": "system",
    "content": "You are a helpful and resourceful virtual shopping assistant" + 
                "specializing in finding the best grocery prices and deals from local supermarkets," + 
                "including Albert Heijn, ALDI, Jumbo, Lidl, Dirk." +
                "You can then receive requests" + 
                "for single items or lists of items and provide a clear table showing price comparisons across these stores." +
                f"You can use the price list from this table below:\n{df_prices.to_string(index=False)}\n"+
                "To the output, Add a column called Lowest Price 💸 populate it with the supermarket where you can get the cheapest deal"+
                "Below the table also provide the links to the product pages from store which has the lowest price "+
                "You can also provide detailed information on the best deals and offers. such as Albert Heijn BONUS, Jumbo EXTRA" +
                " After giving all the details ask them where they usually get their groceries from." +
                " based on their response, give them the savings from sasta ( difference between cost of groceries from the supermarket they usually buy from " +
                " vs the lowest price from the table)"+
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
location_identified = False

# Display postal code in the main app for testing (you can remove this later)
if postal_code == "":
    st.write("Please update your postal code on the sidebar!")

if postal_code != "" and location_identified == False:       
    st.write(f"Your postal code: {postal_code}")

    # Simulate waiting spinner for 2 seconds
    with st.spinner('Locating the nearest stores...'):
        time.sleep(1.5)

    # Add the image
    st.image("shops_nearby.png", caption="Shops near you", use_column_width=True)
    
    
    location_response = "Nice. You have the following shops near you: AH, Lidl, Jumbo, and Aldi near you. Perfect!"
    query = "What do you want to buy today?"

    
    # Display the response and query
    st.write(location_response)
    st.write(query)
    location_identified = True

    with st.spinner('Generating a sample grocery list for you...'):
        time.sleep(1)
        # Display the sample grocery list as a table
        sample_items = df_prices[['Items', 'Qty']].head(5)
        # st.table(sample_items)

        # Create a string version of the table to "copy"
        grocery_list = sample_items.to_string(index=True)
        
        # Button to copy to clipboard
        st.info(
            "You can copy the items to the clipboard by clicking here ↘️")
        st.code(
            grocery_list)

# Initialize session state for the model and messages
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = [system_prompt]  # Add system prompt at the start

# Handle user input and bot responses
if prompt := st.chat_input("What do you want to buy today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        # Simulate waiting spinner for 2 seconds
        with st.spinner('Thinking...'):
            time.sleep(1)
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