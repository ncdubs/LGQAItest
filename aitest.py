import streamlit as st
import openai

# Set up API key securely
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("SKU Identifier (AI-Powered)")

sku_input = st.text_input("Enter a product SKU (e.g., LREL6325F):")

if sku_input:
    with st.spinner("Thinking..."):
        prompt = f"""
        Given the product SKU "{sku_input}", try to identify what type of appliance this is. 
        You can guess the brand if possible (e.g. LG, Samsung, GE) and give a short 2-sentence description.
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # or "gpt-3.5-turbo" for free-tier
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
            )

            result = response.choices[0].message["content"]
            st.success("AI SKU Description:")
            st.write(result)

        except Exception as e:
            st.error(f"Error: {e}")
