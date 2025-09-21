import streamlit as st
import pyodbc
import pandas as pd
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

load_dotenv()


model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

class Query(BaseModel):
    query: str

parser = PydanticOutputParser(pydantic_object=Query)

template = """
You are an AI SQL assistant 🤖. 
Your task is to generate a valid SQL query for table name = {table_name}, based on the column descriptions and the user’s query description. 

- Only return the SQL query as a plain string, no explanations or extra text. 
- SQL operation can be SELECT, INSERT, UPDATE, DELETE. 
- Use proper SQL Server syntax (TOP instead of LIMIT). 
- Do not return anything other than the SQL query string. 

Column description: {column_description} 
Query description: {query_description} 

Return ONLY a JSON object strictly in this format:
{format_instructions}
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["column_description", "query_description", "table_name"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

def get_connection(server, database, username=None, password=None, auth_type="Windows"):
    if auth_type == "Windows":
        return pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={server};'
            f'DATABASE={database};'
            'Trusted_Connection=yes;'
        )
    else:
        return pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
        )

st.set_page_config(layout="wide")
st.title("AI SQL Assistant 🤖")
st.markdown("Use natural language to generate and execute SQL queries. Powered by AI.")

with st.sidebar:
    st.header("🔑 Database Connection")
    
    server = st.text_input("Server Name", value="localhost")
    auth_type = st.radio("Authentication Type", ["Windows", "SQL Server"])
    
    username, password = None, None
    if auth_type == "SQL Server":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
    
    connect_btn = st.button("Connect to Server")
    
if "connected" not in st.session_state:
    st.session_state.connected = False

if connect_btn:
    try:
        conn = get_connection(server, "master", username, password, auth_type)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sys.databases")
        databases = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        st.session_state.databases = databases
        st.session_state.server = server
        st.session_state.username = username
        st.session_state.password = password
        st.session_state.auth_type = auth_type
        st.session_state.connected = True
        st.success("✅ Connected successfully!")
    except Exception as e:
        st.error(f"Connection failed: {e}")
        st.stop()

if st.session_state.connected:
    with st.sidebar:
        selected_db = st.selectbox("Select Database", st.session_state.databases)
        
        try:
            conn = get_connection(st.session_state.server, selected_db,
                                  st.session_state.username, st.session_state.password,
                                  st.session_state.auth_type)
            cursor = conn.cursor()
            cursor.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
            tables = [(row[0], row[1]) for row in cursor.fetchall()]
            cursor.close()
            conn.close()
        except Exception as e:
            st.error(f"Error fetching tables: {e}")
            st.stop()
        
        table_names = [f"{schema}.{table}" for schema, table in tables]
        selected_table = st.selectbox("Select Table", table_names)
    

    st.subheader("📝 Query Assistant")
    try:
        conn = get_connection(st.session_state.server, selected_db,
                              st.session_state.username, st.session_state.password,
                              st.session_state.auth_type)
        cursor = conn.cursor()
        schema, table_name_only = selected_table.split(".")
        cursor.execute(f"SELECT TOP 1 * FROM [{schema}].[{table_name_only}]")
        columns = [col[0] for col in cursor.description]
        st.info(f"Available columns: **{', '.join(columns)}**")
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Error fetching columns: {e}")
        st.stop()
    
    query_input = st.text_area("Enter your question in plain English:", height=100,
                               placeholder="e.g. Show top 10 employees with highest salary.")
    
    if st.button("Generate & Run SQL", type="primary", use_container_width=True):
        if not query_input:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Generating and executing query..."):
                try:
                    formatted_prompt = prompt.format_prompt(
                        column_description=", ".join(columns),
                        query_description=query_input,
                        table_name=table_name_only
                    )
                    result = model.invoke(formatted_prompt.to_string())
                    ai_text = result.content
                    parsed_result = parser.parse(ai_text)
                    sql_query = parsed_result.query
                    
                    st.success("✅ Query generated successfully!")
                    st.code(sql_query, language="sql")
                    
                    conn = get_connection(st.session_state.server, selected_db,
                                          st.session_state.username, st.session_state.password,
                                          st.session_state.auth_type)
                    cursor = conn.cursor()
                    
                    query_type = sql_query.strip().split()[0].upper()
                    if query_type in ["SELECT", "WITH"]:
                        cursor.execute(sql_query)
                        rows = cursor.fetchall()
                        cols = [col[0] for col in cursor.description]
                        df_result = pd.DataFrame.from_records(rows, columns=cols)
                        st.subheader("📊 Query Result")
                        st.dataframe(df_result, use_container_width=True)
                    if query_type in ["INSERT"]:
                        cursor.execute("SET IDENTITY_INSERT Employee ON")
                        cursor.execute(sql_query)
                        conn.commit()
                        st.success(f"✅ `{query_type}` command executed successfully.")
                        cursor.execute("SET IDENTITY_INSERT Employee OFF")
                    else:
                        cursor.execute(sql_query)
                        conn.commit()
                        st.success(f"✅ `{query_type}` command executed successfully.")
                    
                    cursor.close()
                    conn.close()
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.warning("Please try again with a different query.")
