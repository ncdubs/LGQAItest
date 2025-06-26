# Streamlit SKU Matcher with GPT and Tokens

import streamlit as st
import openai
import os

# --- BASIC PASSWORD PROTECTION ---
def login():
    password = st.text_input("Enter Password", type="password")
    if password != os.getenv("APP_PASSWORD"):
        st.warning("Incorrect password.")
        st.stop()

login()

# --- API KEY SETUP ---
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("AI-Powered SKU Matcher")

# --- INPUT ---
sku = st.text_input("Enter Competitor SKU:")
submit = st.button("Find Equivalent")

# --- GPT PROMPT FUNCTIONS ---
def get_competitor_product_info(sku):
    prompt = f"""
    A customer entered this appliance SKU: {sku}.

    1. Identify which brand this SKU belongs to (e.g., Frigidaire, LG, Whirlpool).
    2. Visit that brand's official website.
    3. Locate the product page for this exact SKU.
    4. Return a bullet-point summary of:
       - Brand
       - Product type
       - Dimensions and capacity
       - Key features or configurations
       - **Full list price (MSRP or price before any sales or discounts)**
       - Link to the product page

    ⚠️ Do NOT return a sale price. Only return the original full price if it is shown. If no full price is available, say 'Full price not listed.'
    """

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant skilled at retrieving and summarizing appliance product information."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def get_ge_match(product_summary):
    prompt = f"""
    Based on this competitor product description:

    {product_summary}

    Search GEAppliances.com and recommend the most similar GE product.
    Return:
    - GE product name and model
    - Why it's a good match (compare key features)
    - Product link (if possible)

    Be concise and helpful.
    """

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a product expert skilled at comparing appliances and recommending equivalent GE models."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def generate_comparison_table(competitor_info, ge_match, feature):
    prompt = f"""
    You previously analyzed a competitor appliance and recommended a matching GE product.

    Competitor product:
    {competitor_info}

    GE recommendation:
    {ge_match}

    Return a markdown table comparing the following attributes side-by-side:
    - Brand
    - Price (original MSRP)
    - Size or dimensions
    - Configuration (top control, front load, stackable, etc.)
    - {feature if feature else 'N/A'}
    - Product link

    Format the response as a markdown table like this:

    | Feature       | Competitor Product     | GE Product           |
    |---------------|------------------------|----------------------|
    | Brand         | [brand]                | [brand]              |
    | Price         | [price]                | [price]              |
    | Size          | [size]                 | [size]               |
    | Configuration | [config]               | [config]             |
    | {feature if feature else 'Feature'}     | [value]              | [value]              |
    | Product Link  | [link]                 | [link]               |
    """

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that can compare features between appliances."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# --- MAIN LOGIC ---
specific_feature = None

if submit and sku:
    with st.spinner("Retrieving competitor product info..."):
        competitor_info = get_competitor_product_info(sku)
        st.subheader("Competitor Product Info")
        st.markdown(competitor_info)

    with st.spinner("Finding best GE match..."):
        ge_match = get_ge_match(competitor_info)
        st.subheader("Recommended Equivalent")
        st.markdown(ge_match)

    feature_options = [
        "ADA compliance", "Stainless steel tub", "WiFi connectivity",
        "Energy Star rated", "Top control panel", "Child lock",
        "Third rack", "SmartDry", "Quiet operation", "Steam clean"
    ]
    specific_feature = st.selectbox("Select a specific feature to compare:", feature_options)

    with st.spinner("Generating comparison table..."):
        feature_check = generate_comparison_table(competitor_info, ge_match, specific_feature)
        st.subheader("Feature Comparison Table")
        st.markdown(feature_check)
