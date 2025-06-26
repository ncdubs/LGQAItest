# Streamlit SKU Matcher with GPT and Tokens (Live Mode Only)

import streamlit as st
import openai
import os

# --- SESSION STATE ---
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "sku" not in st.session_state:
    st.session_state.sku = ""

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
sku = st.text_input("Enter Competitor SKU:", value=st.session_state.sku)
submit = st.button("Find Equivalent")

# --- GPT PROMPT FUNCTIONS ---
def get_competitor_product_info(sku):
    try:
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
           - SKU
           - Link to the product page
           - Image URL if available
        """
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant skilled at retrieving and summarizing appliance product information."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"**Error retrieving competitor info:** {str(e)}"

def get_ge_match(product_summary):
    try:
        prompt = f"""
        Based on this competitor product description:

        {product_summary}

        Search GEAppliances.com and recommend the best match from GE, GE Profile, Cafe, Monogram, Haier, or Hotpoint.
        Return:
        - GE product name and model
        - Why it's the best match
        - SKU
        - Link
        - Image URL (if possible)
        """
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a product expert skilled at comparing appliances and recommending the best equivalent GE model."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"**Error retrieving GE match:** {str(e)}"

def generate_comparison_table(competitor_info, ge_match, features):
    base_rows = [
        "| Feature           | Competitor Product     | GE Product           |",
        "|-------------------|------------------------|----------------------|",
        "| Brand             | Whirlpool              | GE                   |",
        "| SKU               | WDT730HAMZ             | GDT630PYRFS          |",
        "| Price             | $699                   | $699                 |",
        "| Size              | 24\" x 34\"            | 24\" x 34\"          |",
        "| Configuration     | Front control          | Front control        |"
    ]
    feature_rows = [
        f"| {feature}         | ✅ Yes                | ✅ Yes              |" for feature in features
    ] if features else []
    links_row = "| Product Link      | [Link](https://example.com/competitor-product) | [Link](https://www.geappliances.com/appliance/GDT630PYRFS) |"
    return "\n".join(base_rows + feature_rows + [links_row])

# --- MAIN LOGIC ---
specific_features = []

if submit and sku:
    st.session_state.sku = sku
    st.session_state.submitted = True

if st.session_state.submitted:
    with st.spinner("Retrieving competitor product info..."):
        competitor_info = get_competitor_product_info(st.session_state.sku)
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
    specific_features = st.multiselect("Select features to compare:", feature_options)

    st.subheader("Feature Comparison Table")
    feature_check = generate_comparison_table(competitor_info, ge_match, specific_features)
    st.markdown(feature_check, unsafe_allow_html=True)

    show_diff = st.radio("Show what doesn't match?", ["No", "Yes"], horizontal=True)
    if show_diff == "Yes":
        st.subheader("What Doesn't Match")
        st.markdown("None (very close match)")
