# Streamlit SKU Matcher with GPT and Tokens (Live Mode Only)

import streamlit as st
import openai
import os
import re

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

# --- UTILITIES ---
def extract_field(text, field):
    """Extracts a value after a dash from a GPT bullet point line."""
    lines = text.split('\n')
    for line in lines:
        if field.lower() in line.lower():
            parts = line.split("-", 1)
            if len(parts) == 2:
                return parts[1].strip()
    return "Not listed"

def estimate_msrp_from_text(text):
    """Estimate MSRP from sale price + savings if available, else extract MSRP directly."""
    try:
        sale_match = re.search(r'\$([\d,]+).*save[s]?[\s\S]*?\$([\d,]+)', text, re.IGNORECASE)
        if sale_match:
            sale = int(sale_match.group(1).replace(",", ""))
            savings = int(sale_match.group(2).replace(",", ""))
            return f"${sale + savings} (estimated)"
        msrp_match = re.search(r'(MSRP|list price).*?\$([\d,]+)', text, re.IGNORECASE)
        if msrp_match:
            return f"${msrp_match.group(2)}"
    except:
        pass
    return "Not listed"

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

        Search GEAppliances.com and recommend the best match from GE, GE Profile, Cafe, Monogram, Haier, or Hotpoint. Make sure the product is currently available and not marked as 'no longer being manufactured' or 'discontinued'.
        Return:
        - GE product name and model
        - Confirm that it is currently available and not discontinued
        - Why it's the best match
        - SKU
        - Link
        - Image URL (try to retrieve the first product image or use the og:image meta tag if available)
        - MSRP (If only the sale price and discount are listed, estimate MSRP = sale price + savings)
        - Current sale price
        - Savings (dollar or percent if available)
        """
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a product expert skilled at comparing appliances and recommending the best equivalent GE model."},
                {"role": "user", "content": prompt}
            ]
        )
        raw_output = response.choices[0].message.content

        verify_prompt = f"""
        Is the following GE appliance currently available and not discontinued?

        {raw_output}

        Answer Yes or No only.
        """
        verify = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": verify_prompt}
            ]
        ).choices[0].message.content.strip().lower()

        if "no" in verify:
            retry_prompt = f"""
            Based on this competitor product description:

            {product_summary}

            The last GE recommendation was discontinued. Recommend a different GE product from GE, GE Profile, Cafe, Monogram, Haier, or Hotpoint that is similar and currently available.

            DO NOT recommend discontinued or unavailable products.
            ONLY return products that are currently listed on GEAppliances.com and actively available for sale.
            If uncertain about availability, do not include it.

            Return:
            - GE product name and model
            - Why it's the best match
            - SKU
            - Link
            - Image URL (if possible)
            """
            retry_response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a product expert skilled at comparing appliances and recommending the best equivalent GE model."},
                    {"role": "user", "content": retry_prompt}
                ]
            )
            return retry_response.choices[0].message.content
        return raw_output
    except Exception as e:
        return f"**Error retrieving GE match:** {str(e)}"

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

    st.image([
        extract_field(competitor_info, "Image URL"),
        extract_field(ge_match, "Image URL")
    ], width=300, caption=["Competitor Product", "GE Product"])

    smart_features = {
        "Dishwasher": ["ADA compliance", "Stainless steel tub", "Top control panel", "Child lock", "Third rack", "SmartDry", "Quiet operation", "Steam clean"],
        "Refrigerator": ["ADA compliance", "WiFi connectivity", "Energy Star rated", "Ice maker", "Water dispenser", "Door-in-door", "Adjustable shelves", "Temperature zones", "Freezer drawer"],
        "Washer": ["ADA compliance", "Stackable", "Front load", "Top load", "Steam wash", "SmartDispense", "Sanitize cycle", "WiFi connectivity", "Energy Star rated"],
        "Dryer": ["ADA compliance", "Stackable", "Gas or Electric", "Steam refresh", "Sensor dry", "Wrinkle care", "Smart features", "Sanitize cycle"],
        "Range": ["ADA compliance", "Convection oven", "Air fry", "Double oven", "Self-clean", "Griddle", "Induction cooktop", "Smart control"],
        "Microwave": ["ADA compliance", "Sensor cooking", "Convection option", "Over-the-range", "Built-in", "Child lock", "Quick reheat"],
        "Wall Oven": ["ADA compliance", "Double oven", "Convection", "Self-cleaning", "Steam bake", "WiFi control", "Touchscreen"],
        "Cooktop": ["ADA compliance", "Induction", "Gas", "Electric coil", "Bridge element", "Knob or touch controls", "Power boil"],
        "Freezer": ["ADA compliance", "Upright", "Chest", "Frost-free", "Garage ready", "Temperature alarm", "LED lighting"],
        "Air Conditioner": ["ADA compliance", "Portable", "Window-mounted", "Dehumidifier mode", "Smart thermostat", "Energy saver", "Remote control"],
        "Wine Cooler": ["ADA compliance", "Dual zone", "Built-in or freestanding", "UV protection", "Humidity control", "Quiet compressor"],
        "Icemaker": ["ADA compliance", "Built-in", "Freestanding", "Clear cube ice", "Daily production rate", "Storage capacity"],
        "Laundry Center / Combo": ["ADA compliance", "Stackable", "All-in-one", "Steam wash", "Sensor dry", "WiFi connectivity", "Space-saving design"],
        "Trash Compactor": ["ADA compliance", "Touch-toe drawer", "Odor control", "Air filter", "Stainless steel construction", "Removable key lock"],
        "Garbage Disposal": ["ADA compliance", "Continuous feed", "Batch feed", "Stainless steel grind components", "Sound insulation", "Septic safe"]
    }

    detected_type = "Refrigerator"
    for appliance_type in smart_features.keys():
        if appliance_type.lower() in competitor_info.lower():
            detected_type = appliance_type
            break

    feature_options = smart_features.get(detected_type, [])

    selected_features = st.multiselect("Select features to compare:", feature_options)
    other_feature = st.text_input("Or enter another feature you'd like to compare:")
    if other_feature:
        selected_features.append(other_feature)

    st.subheader("Feature Comparison Table")
    def generate_comparison_table(competitor_info, ge_match, features):
        base_rows = [
            "| Feature           | Competitor Product     | GE Product           |",
            "|-------------------|------------------------|----------------------|"
        ]
        feature_rows = []
        for feature in features:
            value1 = extract_field(competitor_info, feature)
            value2 = extract_field(ge_match, feature)
            feature_rows.append(f"| {feature} | {value1} | {value2} |")
        base_fields = [
            f"| Brand             | {extract_field(competitor_info, 'Brand')} | {extract_field(ge_match, 'Brand')} |",
            f"| SKU               | {extract_field(competitor_info, 'SKU')} | {extract_field(ge_match, 'SKU')} |",
            f"| Price             | {estimate_msrp_from_text(competitor_info)} | {estimate_msrp_from_text(ge_match)} |",
            f"| Size              | {extract_field(competitor_info, 'Dimensions')} | {extract_field(ge_match, 'Dimensions')} |",
            f"| Configuration     | {extract_field(competitor_info, 'Key features')} | {extract_field(ge_match, 'Key features')} |",
            f"| Product Link      | {extract_field(competitor_info, 'Link')} | {extract_field(ge_match, 'Link')} |"
        ]
        return "
".join(base_rows + base_fields + feature_rows).join(base_rows + base_fields + feature_rows)

    st.markdown(generate_comparison_table(competitor_info, ge_match, selected_features), unsafe_allow_html=True)

    show_diff = st.radio("Show what doesn't match?", ["No", "Yes"], horizontal=True)
    if show_diff == "Yes":
        st.subheader("What Doesn't Match")
        from textwrap import dedent
        prompt = dedent(f"""
        Compare the following two appliance descriptions. Write a concise paragraph summarizing what key features do NOT match or differ between them.

        Competitor Product:
        {competitor_info}

        GE Match:
        {ge_match}

        Be clear and use simple language. Mention features that are included in one product but not the other.
        """)
        try:
            diff_response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that identifies key differences in appliance specifications."},
                    {"role": "user", "content": prompt}
                ]
            )
            st.markdown(diff_response.choices[0].message.content)
        except Exception as e:
            st.error(f"Error comparing differences: {e}")

        user_question = st.text_input("Enter a feature to compare (e.g., ADA compliance, noise level)")
        if user_question:
            follow_up_prompt = f"""
            A user is comparing two appliances and wants to know the specific difference related to: {user_question}.

            Competitor Product:
            {competitor_info}

            GE Match:
            {ge_match}

            Give a short and clear answer describing whether the feature exists in both, only one, or neither product.
            """
            try:
                clarification_response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You help identify appliance feature differences clearly."},
                        {"role": "user", "content": follow_up_prompt}
                    ]
                )
                st.markdown(clarification_response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error fetching specific feature info: {e}")
