from openai import OpenAI
import streamlit as st
import streamlit.components.v1 as components
from component import map
import time
import pandas as pd
import re
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from elevenlabs import play, stream, save
from product_match import match_products

from geocode import generate_map

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
eleven_client = ElevenLabs(api_key=st.secrets["ELEVEN_LABS_KEY"])

def display_map(html_file):
    # Read the content of the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        map_html = file.read()

    # Display the HTML content in Streamlit
    components.html(map_html, height=600, scrolling=True)

# Load the CSV file
df_prices = pd.read_csv("sample_prices.csv")

st.title("sasta")
st.subheader("find the best grocery deals near you")

# Define the system prompt to guide the bot's personality
system_prompt = {
    "role": "system",
    "content":  " You are a resourceful virtual grocery shopping assistant speaks usually in english" + 
                " You specialize in finding the best prices and deals from local supermarkets in the Netherlands," + 
                " including Albert Heijn, ALDI, Jumbo, Lidl, Dirk." +
                " You can receive requests of two kinds." + 
                " Sometime the user will give you a receipe/receipes, in that case, you should list down all the groceries required ( this one should be in dutch) for making that dish(es)for 2 people" +
                " In such cases, always produce a table with these 3 columns ingredients , amount (in grams, liters or stuks or other units), quantity (1 by default) and ask the user to confirm."+
                " The header should be in english, the content should be in dutch. If there are"+
                " changes accomodate that through conversation. Wait for user to confirm the ingredients"
                
}

# Sidebar input for postal code
with st.sidebar:
    st.header("Your Location")
    postal_code = st.text_input("Enter your postal code", value="")

location_identified = False
list_confirmed = False

# Display postal code in the main app for testing (you can remove this later)
if postal_code == "":
    st.write("Please update your postal code on the sidebar!")

if postal_code != "" and location_identified == False:       
    st.write(f"Your postal code: {postal_code}")
    with st.spinner('Locating the nearest stores...'):
        generate_map(postal_code, st.secrets["GOOGLE_MAPS_KEY"])

        html_file = "supermarkets_map.html"
        display_map(html_file)
    
    location_response = "Here you go, these are the grocery shops near you!"
    query = "What do you want to buy/cook today?"

    st.write(query)
    location_identified = True

# Initialize session state for the model and messages
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = [system_prompt]  # Add system prompt at the start


if "ingredients_df" not in st.session_state:
    st.session_state.ingredients_df = None

if "show_confirm_button" not in st.session_state:
    st.session_state.show_confirm_button = False

# Handle user input and bot responses
if prompt := st.chat_input("What do you want to buy today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        with st.spinner('Thinking...'):
            time.sleep(1)
        st.markdown(prompt)
    # Add a system prompt at the end of the messages
    st.session_state.messages.append({
        "role": "system",
        "content": "Now that the user has provided their shopping list, please analyze it and provide a detailed price comparison across different supermarkets. Include a column for the lowest price and highlight the best deals. After the comparison, ask about their usual shopping location and calculate potential savings."
    })

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
        
        # Extract ingredients table from the response
        table_match = re.search(r'\|.*\|', response, re.DOTALL)
        if table_match:
            table_text = table_match.group(0)
            lines = table_text.split('\n')
            headers = [header.strip() for header in lines[0].split('|') if header.strip()]
            data = []
            for line in lines[2:]:  # Skip the header separator line
                row = [cell.strip() for cell in line.split('|') if cell.strip()]
                if row:
                    data.append(row)
            
            st.session_state.ingredients_df = pd.DataFrame(data, columns=headers)
            st.session_state.show_confirm_button = True
        else:
            st.session_state.show_confirm_button = False

    st.session_state.messages.append({"role": "assistant", "content": response})

# Add a confirmation button only if ingredients are available
if st.session_state.show_confirm_button:
    if st.button("Confirm Ingredients"):
        if st.session_state.ingredients_df is not None:
            st.write("Ingredients confirmed:")

            st.dataframe(st.session_state.ingredients_df)
            result_df = match_products(st.session_state.ingredients_df)
            # st.write("Top picks from the database (Needs pruning)..")
            # st.dataframe(result_df)

            st.session_state.messages.append({
                "role": "system",
                "content": "Now that the table is here:" +
                result_df.to_string() +               
                "Analyze it and provide a Lowest price for the products across different supermarkets in a table (columns: Product, Sasta Price, Supermarket Picked)."+
                "After the comparison, ask about their usual shopping location and calculate potential savings."
            })

            stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
            )
            response = st.write_stream(stream)


            print("Confirmed Ingredients DataFrame:")
            print(st.session_state.ingredients_df)
        else:
            st.write("No ingredients to confirm. Please ask for a recipe first.")