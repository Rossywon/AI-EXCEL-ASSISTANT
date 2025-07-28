import streamlit as st
import pandas as pd
from openai import OpenAI
import io
import datetime
import matplotlib.pyplot as plt

# ----------------------------
# GROQ API Setup
# ----------------------------
client = OpenAI(api_key=st.secrets["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="AI Excel Assistant", layout="wide")
st.title("🤖 AI Excel Assistant")
st.write("Upload an Excel or CSV file, choose an analysis task, or ask your own question!")

# ----------------------------
# File Upload
# ----------------------------
uploaded_file = st.file_uploader("Upload Excel or CSV", type=["xlsx", "csv"])

if uploaded_file is not None:
    # Load Data
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("📊 Data Preview")
    st.dataframe(df.head())

    # ----------------------------
    # Smart Suggestions
    # ----------------------------
    numeric_cols = df.select_dtypes(include=['float', 'int']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    suggestions = ["Show summary statistics", "Count the number of rows and columns"]
    if numeric_cols and categorical_cols:
        suggestions.append(f"Calculate total {numeric_cols[0]} by {categorical_cols[0]}")
        suggestions.append(f"Calculate average {numeric_cols[0]} by {categorical_cols[0]}")
    if numeric_cols:
        suggestions.append(f"Show top 5 rows by {numeric_cols[0]}")
    if categorical_cols:
        suggestions.append(f"List unique values in {categorical_cols[0]}")

    st.subheader("💡 Smart Suggestions")
    selected_option = st.selectbox("Choose a suggested task:", suggestions)

    st.subheader("✍️ Or enter your own command")
    command = st.text_input("Example: 'Summarize total sales by region'", value=selected_option)

    chart_type = st.selectbox("📊 Select Chart Type (Optional)", ["None", "Bar Chart", "Line Chart", "Area Chart", "Pie Chart"])

    # ----------------------------
    # AI Analysis
    # ----------------------------
    if st.button("Run Command"):
        if command.strip() != "":
            with st.spinner("Analyzing..."):
                prompt = f"""
                You are a Python data analysis assistant.
                The user uploaded a dataset with these columns: {list(df.columns)}.
                Task: {command}.
                Write Python Pandas code that uses the DataFrame 'df' to achieve this task.
                Store the final result in a variable named 'result'. Do not include explanations.
                """

                try:
                    # AI generates code
                    response = client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=[
                            {"role": "system", "content": "You are an expert Python and Pandas data analyst."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0
                    )

                    code = response.choices[0].message.content
                    code = code.replace("```python", "").replace("```", "").strip()

                    # Display Generated Code
                    st.subheader("🔍 Generated Code:")
                    st.code(code, language="python")

                    # Execute Code
                    local_env = {'df': df, 'pd': pd}
                    exec(code, {}, local_env)

                    if 'result' in local_env:
                        result = local_env['result']
                        st.subheader("✅ Result:")
                        if isinstance(result, (pd.DataFrame, pd.Series)):
                            st.dataframe(result)
                        else:
                            st.write(result)

                        # ----------------------------
                        # Visualization
                        # ----------------------------
                        if chart_type != "None" and isinstance(result, (pd.Series, pd.DataFrame)):
                            st.subheader(f"📊 {chart_type}")
                            if chart_type in ["Bar Chart", "Line Chart", "Area Chart"]:
                                if isinstance(result, pd.Series):
                                    if chart_type == "Bar Chart":
                                        st.bar_chart(result)
                                    elif chart_type == "Line Chart":
                                        st.line_chart(result)
                                    elif chart_type == "Area Chart":
                                        st.area_chart(result)
                                elif isinstance(result, pd.DataFrame) and result.shape[1] >= 2:
                                    numeric_cols_result = result.select_dtypes(include=['float', 'int']).columns
                                    if len(numeric_cols_result) >= 1:
                                        chart_data = result.set_index(result.columns[0])[numeric_cols_result[0]]
                                        if chart_type == "Bar Chart":
                                            st.bar_chart(chart_data)
                                        elif chart_type == "Line Chart":
                                            st.line_chart(chart_data)
                                        elif chart_type == "Area Chart":
                                            st.area_chart(chart_data)
                            elif chart_type == "Pie Chart":
                                fig, ax = plt.subplots()
                                if isinstance(result, pd.Series):
                                    result.plot.pie(autopct='%1.1f%%', ax=ax)
                                elif isinstance(result, pd.DataFrame) and result.shape[1] >= 2:
                                    numeric_cols_result = result.select_dtypes(include=['float', 'int']).columns
                                    if len(numeric_cols_result) >= 1:
                                        pie_data = result.set_index(result.columns[0])[numeric_cols_result[0]]
                                        pie_data.plot.pie(autopct='%1.1f%%', ax=ax)
                                st.pyplot(fig)

                        # ----------------------------
                        # Download Buttons
                        # ----------------------------
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        if isinstance(result, pd.DataFrame):
                            excel_buffer = io.BytesIO()
                            result.to_excel(excel_buffer, index=False)
                            st.download_button(
                                label="⬇ Download as Excel",
                                data=excel_buffer.getvalue(),
                                file_name=f"analysis_result_{timestamp}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                            csv_buffer = io.StringIO()
                            result.to_csv(csv_buffer, index=False)
                            st.download_button(
                                label="⬇ Download as CSV",
                                data=csv_buffer.getvalue(),
                                file_name=f"analysis_result_{timestamp}.csv",
                                mime="text/csv"
                            )
                        elif isinstance(result, pd.Series):
                            csv_buffer = io.StringIO()
                            result.to_csv(csv_buffer)
                            st.download_button(
                                label="⬇ Download as CSV (Series)",
                                data=csv_buffer.getvalue(),
                                file_name=f"analysis_result_{timestamp}.csv",
                                mime="text/csv"
                            )
                        else:
                            st.download_button(
                                label="⬇ Download as Text",
                                data=str(result),
                                file_name=f"analysis_result_{timestamp}.txt",
                                mime="text/plain"
                            )

                    # AI Summary
                    summary_prompt = f"Summarize these findings in 2-3 sentences for a business audience:\n{str(result)[:1500]}"
                    summary_response = client.chat.completions.create(
                        model="llama3-70b-8192",
                        messages=[
                            {"role": "system", "content": "You are a business data analyst. Provide concise insights."},
                            {"role": "user", "content": summary_prompt}
                        ]
                    )
                    st.subheader("💡 AI Insights")
                    st.write(summary_response.choices[0].message.content)

                except Exception as e:
                    st.error(f"Error: {e}")

# ----------------------------
# Excel Formula Generator
# ----------------------------
st.markdown("---")
st.header("📄 Excel Formula Generator")

excel_question = st.text_input("Enter your Excel formula question", placeholder="Example: Formula for CAGR")

if st.button("Generate Formula"):
    if excel_question.strip() != "":
        with st.spinner("Generating Excel formula..."):
            try:
                formula_prompt = f"""
                You are an Excel expert. The user asked: {excel_question}.
                Provide:
                1. The correct Excel formula
                2. A short explanation of what it does
                3. An example if needed
                """
                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": "You are an Excel expert helping users with formulas."},
                        {"role": "user", "content": formula_prompt}
                    ],
                    temperature=0
                )
                answer = response.choices[0].message.content
                st.subheader("✅ Excel Formula Answer")
                st.write(answer)
            except Exception as e:
                st.error(f"Error: {e}")
