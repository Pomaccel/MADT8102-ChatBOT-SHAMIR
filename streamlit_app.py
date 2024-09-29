import streamlit as st
import google.generativeai as genai
import langchain
from langchain.llms import OpenAI
from google.cloud import bigquery
import re

# Create by Bunrawat Charoenyuennan DADS
st.title("👨‍💼 Data Analyst Chatbot")
st.subheader("Presented By Bunrawat Charoenyuennan")

# Capture Gemini API Key
gemini_api_key = st.text_input("Gemini API Key: ", placeholder="Type your API Key here...", type="password")

# Initialize the Gemini Model
if gemini_api_key:
    try:
        # Configure Gemini with the provided API Key
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-pro")
        st.success("Gemini API Key successfully configured.")
    except Exception as e:
        st.error(f"An error occurred while setting up the Gemini model: {e}")

# Initialize session state for storing chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Initialize with an empty list

# Display previous chat history
for role, message in st.session_state.chat_history:
    st.chat_message(role).markdown(message)

# Welcome message for the first interaction
if len(st.session_state.chat_history) == 0:
    welcome_message = (
        "Hello! I'm your friendly Professional Data Analyst. "
        "Feel free to ask me about any data analysis, and I'll translate it into actionable insights!"
    )
    st.session_state.chat_history.append(("assistant", welcome_message))
    st.chat_message("assistant").markdown(welcome_message)

# Function to detect gratitude in user input
def detect_gratitude(user_input):
    gratitude_keywords = [
        "thank you", "thanks", "thx", "cheers", "much appreciated",
        "thank", "appreciate", "grateful", "gratitude"
    ]
    pattern = re.compile(r"\b(" + "|".join(gratitude_keywords) + r")\b", re.IGNORECASE)
    return bool(pattern.search(user_input))

# AI Agent 1: Translate User Inquiry to SQL using NLP and LangChain
def agent_1_translate_to_sql(user_input):
    # Example of using LangChain for NLP and LLM-driven translations
    llm = OpenAI(temperature=0)  # Using OpenAI or another LLM for query translation
    chain = langchain.LLMChain(llm=llm)
    prompt = f"Translate the following user request into an SQL query: {user_input}"
    sql_query = chain.run(prompt)
    return sql_query

# AI Agent 2: Query Google BigQuery
def agent_2_query_bigquery(sql_query):
    client = bigquery.Client(project="chat-bot-436611")
    dataset_id = "Coffee"
    table_id = "Coffee_sale"
    full_table_id = f"{dataset_id}.{table_id}"

    try:
        # Querying BigQuery with the SQL Query
        query_job = client.query(sql_query)
        results = query_job.result()
        return results
    except Exception as e:
        st.error(f"An error occurred while querying BigQuery: {e}")
        return None

# AI Agent 3: Convert BigQuery Result to Friendly Response using Gemini AI
def agent_3_generate_friendly_response(query_results):
    # Convert the query results into a human-readable response
    results_text = "\n".join([str(row) for row in query_results]) if query_results else "No data found."
    
    if model:
        try:
            query = f"Here are the query results: {results_text}. Please convert this into a friendly response."
            response = model.generate_content(query)
            return response.text
        except Exception as e:
            return f"An error occurred while generating the response: {e}"
    return results_text

# Capture user input and generate bot response
if user_input := st.chat_input("Ask me a data-related question..."):
    # Store and display user message
    st.session_state.chat_history.append(("user", user_input))
    st.chat_message("user").markdown(user_input)

    # Check for gratitude and stop recommending if detected
    if detect_gratitude(user_input):
        bot_response = "You're welcome! 😊 If you need any more help, feel free to ask!"
    else:
        try:
            # AI Agent 1: Translate User Input to SQL
            sql_query = agent_1_translate_to_sql(user_input)
            st.session_state.chat_history.append(("assistant", f"Generated SQL: {sql_query}"))
            st.chat_message("assistant").markdown(f"Generated SQL: {sql_query}")

            # AI Agent 2: Query BigQuery
            query_results = agent_2_query_bigquery(sql_query)

            # AI Agent 3: Convert the result to a friendly response
            bot_response = agent_3_generate_friendly_response(query_results)
        except Exception as e:
            bot_response = f"An error occurred: {e}"

    # Store and display the bot response
    st.session_state.chat_history.append(("assistant", bot_response))
    st.chat_message("assistant").markdown(bot_response)
