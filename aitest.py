# Streamlit SKU Matcher with GPT and Tokens (Demo Mode)

import streamlit as st
import openai
import os

# --- MODE TOGGLE ---
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

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
if not DEMO_MODE:
    openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("AI-Powered SKU Matcher (Demo Mode Enabled)" if DEMO_MODE else "AI-Powered SKU Matcher")

# --- INPUT ---
sku = st.text_input("Enter Competitor SKU:", value=st.session_state.sku)
submit = st.button("Find Equivalent")

# --- GPT PROMPT FUNCTIONS ---
def get_competitor_product_info(sku):
    if DEMO_MODE:
        return f"""
        - Brand: Whirlpool  
        - Product type: Dishwasher  
        - Dimensions: 24\"W x 34\"H  
        - Key features: Stainless steel tub, Quiet operation  
        - Full list price: $699  
        - SKU: WDT730HAMZ  
        - Link: https://example.com/competitor-product
        """
    # GPT logic here...


def get_ge_match(product_summary):
    if DEMO_MODE:
        return f"GE Model: GDT630PYRFS  \nWhy it matches: Same size, stainless tub, quiet features  \nSKU: GDT630PYRFS  \nLink: https://www.geappliances.com/appliance/GDT630PYRFS"
    # GPT logic here...


def generate_comparison_table(competitor_info, ge_match, feature):
    if DEMO_MODE:
        return f"""
        | Feature           | Competitor Product     | GE Product           |
        |-------------------|------------------------|----------------------|
        | Brand             | Whirlpool              | GE                   |
        | SKU               | WDT730HAMZ             | GDT630PYRFS          |
        | Price             | $699                   | $699                 |
        | Size              | 24\" x 34\"            | 24\" x 34\"          |
        | Configuration     | Front control          | Front control        |
        | {feature}         | Yes                    | Yes                  |
        | Product Link      | [Link](https://example.com/competitor-product) | [Link](https://www.geappliances.com/appliance/GDT630PYRFS) |
        | What Doesn't Match | None (very close match) | None (very close match) |
        """
    # GPT logic here...

# --- MAIN LOGIC ---
specific_feature = None

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
    specific_feature = st.selectbox("Select a specific feature to compare:", feature_options)

    if specific_feature:
        with st.spinner("Generating comparison table..."):
            feature_check = generate_comparison_table(competitor_info, ge_match, specific_feature)
            st.subheader("Feature Comparison Table")
            st.markdown(feature_check)
