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
    "content":  " You are a resourceful virtual grocery shopping assistant" + 
                " You specialize in finding the best prices and deals from local supermarkets in the Netherlands," + 
                " including Albert Heijn, ALDI, Jumbo, Lidl, Dirk." +
                " You can receive requests of two kinds." + 
                " Sometime the user will give you a receipe, in that case, you should list down the groceries required for making that dish(es) for 2 people" +
                " In such cases, ensure that you produce a table (with these 3 columns) ingredients , amount (in grams, liters or stuks or other units), quantity and ask the user to confirm."+
                " The header should be in english, the content should be in dutch. If there are"+
                " changes accomodate that through conversation." +
                " Then use that table to find the best prices across supermarket." +
                " If the user inputs single items or lists of items and provide a clear table showing price comparisons across these stores." +
                " To the output, Add a column called Lowest Price 💸 populate it with the supermarket where you can get lowest price"+
                " Below the table also provide the links to the product pages from store which has the lowest price "+
                " You can also provide detailed information on the best deals and offers. such as Albert Heijn BONUS, Jumbo EXTRA" +
                " After giving all the details ask them where they usually get their groceries from." +
                " based on their response, calculate savings (current supermarket vs the lowest price from the table)"+
                " and also the monthly savings (how much they could potentially save per month) by multiplying the above number by 4" +
                " Once you give this figure, ask for a call to action to signup using this link: https://form.jotform.com/242401875157356"
                " Your tone is friendly, professional, and efficient, helping users save time and money on their grocery shopping." + 
                " Whenever possible, you offer additional tips for budget-friendly choices and seasonal discounts."
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
            st.write("Top picks from the database (Needs pruning)..")
            st.dataframe(result_df)

            print("Confirmed Ingredients DataFrame:")
            print(st.session_state.ingredients_df)
        else:
            st.write("No ingredients to confirm. Please ask for a recipe first.")