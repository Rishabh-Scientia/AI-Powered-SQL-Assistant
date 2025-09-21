# 🧑‍💻 AI-Powered SQL Assistant

An **AI-driven SQL Query Generator and Executor** that allows you to interact with your **SQL Server database** using natural language. Built with **Streamlit, LangChain, and Google Gemini**, this app converts plain English into SQL queries, executes them, and displays results in a clean UI.

---

## 🚀 Features

- 🔗 **Database Connection** – Connect to SQL Server by entering server, username, password, and database.  
- 📂 **Explore Schema** – View available databases, tables, and their columns.  
- 🧠 **AI Query Generation** – Convert natural language into SQL Server–compatible queries.  
- ▶️ **Execute Queries** – Run `SELECT`, `INSERT`, `UPDATE`, `DELETE` queries directly.  
- 📊 **Results Display** – Get query results as interactive dataframes in Streamlit.  
- ⚡ **Error Handling** – Gracefully handles SQL errors and invalid queries.  

---

## 🛠️ Tech Stack

- **Python**
  - Streamlit  
  - PyODBC  
  - Pandas  
- **LangChain** – prompt handling + LLM integration  
- **LLM MODEL** – natural language → SQL conversion  
- **SQL Server** – database backend  

---

## 📌 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/sql-ai-assistant.git
   cd sql-ai-assistant
2. **Create virtual environment**
   python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
3. **Install dependencies**
   pip install -r requirements.txt
4. **Set up environment variables**
   Create a .env file and add your LLM API key:
5. **Run the app**
   streamlit run filename.py

## 🖥️ Usage

1. **Launch the app.**
2. **Enter your SQL Server credentials.**
3. **Select the database and explore tables.**
4. **Type a natural language query, e.g.:**
   Show me the average salary by department
5. **The AI generates a valid SQL query and executes it.**
6. **View results instantly in the Streamlit UI.**

## 🔮 Future Improvements

**✅ Advanced Querying – Enable support for joins, nested queries, and more complex SQL operations.**

**🌐 Multi-Database Support – Extend compatibility beyond SQL Server to include MySQL and PostgreSQL.**

**🔐 Role-Based Access Control – Add authentication and permissions for different user roles (Admin, Analyst, Viewer).**

**📊 Export Options – Allow users to export query results directly as CSV or Excel files for reporting.**

## 🤝 Contributing
 **Contributions are welcome! Feel free to fork the repo, create a new branch, and submit a pull request.**

## 📜 License**

This project is licensed under the MIT License.
