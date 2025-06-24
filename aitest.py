import streamlit as st
import openai

# 🔐 Load OpenAI API key from secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ✅ Initialize the OpenAI client
client = openai.OpenAI(api_key=openai.api_key)

# 🎯 Title and instructions
st.title("SKU Identifier (AI-Powered)")
sku_input = st.text_input("Enter a product SKU (e.g., LREL6325F):")

if sku_input:
    try:
        # 🧠 Build the prompt
        prompt = f"What brand is the product with SKU '{sku_input}'? Please only return the brand name or say 'Unknown' if you cannot determine it."

        # 📡 Call OpenAI's API using new v1.0+ format
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You're a product data assistant. Respond only with brand names if possible."},
                {"role": "user", "content": prompt}
            ]
        )

        result = response.choices[0].message.content.strip()
        st.success(f"🧾 Detected Brand: **{result}**")

    except Exception as e:
        st.error(f"Error: {e}")
