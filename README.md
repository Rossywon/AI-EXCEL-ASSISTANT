🤖 AI Excel Assistant
AI Excel Assistant is a Streamlit-based app that helps you analyze Excel or CSV data using AI-powered insights and perform smart analytics without writing code.
You can upload your dataset, choose a suggested analysis, ask custom questions, visualize results, and even generate Excel formulas automatically.

🌐 Live Demo
👉 Copy link: https://ai-excel-assistant-oafc5wvmtgedgbxftjujpp.streamlit.app/

✅ Features
Upload Excel/CSV files and preview data.

AI-Powered Analysis: Ask natural language questions like:

"Summarize total sales by region"

"Show average revenue per product category"

Smart Suggestions Dropdown for quick analysis.

Auto-generated charts (Bar & Pie).

Excel Formula Generator – get accurate formulas and explanations.

Download Results as Excel or CSV.

🛠 Tech Stack
Python 3.9+

Streamlit for the web app

Pandas for data handling

Groq API for AI analysis

Matplotlib 

🚀 How to Run Locally
1. Clone this repository
git clone https://github.com/Rossywon/AI-EXCEL-ASSISTANT.git
cd AI-EXCEL-ASSISTANT

2. Install dependencies

pip install -r requirements.txt

3. Run the Streamlit app
streamlit run app.py

🛠 Requirements
Your requirements.txt includes:
streamlit==1.47.1
pandas==2.3.1
openai==1.97.1
matplotlib==3.9.2
openpyxl==3.1.5

🔐 API Key Setup
The app uses Groq API (OpenAI-compatible).
Add your key like this in the code:

API_KEY = "your_api_key_here"
client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

💡 Example Commands
"Summarize total sales by region"

"Show top 10 products by revenue"

"Calculate average discount per category"
-----To-Do
 Add support for multiple charts per query

 Implement dark mode UI

 Add Google Sheets integration

 contact:
 email:rosewonah@gmail.com
 Phone:07039025651



