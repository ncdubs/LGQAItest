import streamlit as st
import openai
import os

# 🧠 Set OpenAI API key securely
openai.api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# 🧾 App title
st.title("🔍 SKU Product Recognizer")
st.markdown("Enter any product SKU below. This tool will use AI to recognize the product, its brand, and type.")

# 🧠 User input
sku_input = st.text_input("Enter a product SKU:")

# 📦 Prompt template
sku_lookup_prompt = f"""
You are a product analyst assistant. Given the following SKU, determine the brand and the general product type (e.g., refrigerator, dryer, gas range, etc.).
Return the result in the following format:
Brand: <brand>
Type: <type>

SKU: {sku_input}
"""

# ▶️ Run GPT call
if sku_input:
    with st.spinner("Analyzing SKU with AI..."):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # You can use "gpt-3.5-turbo" if preferred
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that classifies product SKUs."},
                    {"role": "user", "content": sku_lookup_prompt}
                ]
            )
            result = response.choices[0].message['content']
            st.success("AI successfully analyzed the SKU")
            st.code(result, language="markdown")
        except Exception as e:
            st.error(f"Error: {e}")
