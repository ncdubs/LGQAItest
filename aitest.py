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
        "| Brand             | [Brand Placeholder]    | [Brand Placeholder]  |",
        "| SKU               | [SKU1]                 | [SKU2]               |",
        "| Price             | [Price1]               | [Price2]             |",
        "| Size              | [Size1]                | [Size2]              |",
        "| Configuration     | [Config1]              | [Config2]            |"
    ]
    feature_rows = [
        f"| {feature}         | ✅ Yes                | ❌ No               |" if feature == "ADA compliance" else f"| {feature}         | Text from Competitor   | Text from GE         |"
        for feature in features
    ] if features else []
    links_row = "| Product Link      | [Link1]                | [Link2]               |"
    return "\n".join(base_rows + feature_rows + [links_row])

def generate_differences_table():
    return """
    | Feature               | Competitor Product       | GE Product               |
    |------------------------|---------------------------|--------------------------|
    | ADA compliance         | ✅ Yes                    | ❌ No                   |
    | Stainless steel tub    | ✅ Yes                    | ✅ Yes                  |
    | Third rack             | ❌ No                     | ✅ Yes                  |
    | Noise level            | 44 dBA                    | 50 dBA                  |
    | Steam cycle            | Not listed                | ✅ Included             |
    """

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
        "https://example.com/competitor_image.jpg",
        "https://example.com/ge_image.jpg"
    ], width=300, caption=["Competitor Product", "GE Product"])

    # Smart feature suggestions by product type
    smart_features = {
        "Dishwasher": [
            "ADA compliance", "Stainless steel tub", "Top control panel",
            "Child lock", "Third rack", "SmartDry", "Quiet operation", "Steam clean"
        ],
        "Refrigerator": [
            "ADA compliance", "WiFi connectivity", "Energy Star rated", "Ice maker",
            "Water dispenser", "Door-in-door", "Adjustable shelves", "Temperature zones", "Freezer drawer"
        ],
        "Washer": [
            "ADA compliance", "Stackable", "Front load", "Top load", "Steam wash",
            "SmartDispense", "Sanitize cycle", "WiFi connectivity", "Energy Star rated"
        ],
        "Dryer": [
            "ADA compliance", "Stackable", "Gas or Electric", "Steam refresh",
            "Sensor dry", "Wrinkle care", "Smart features", "Sanitize cycle"
        ],
        "Range": [
            "ADA compliance", "Convection oven", "Air fry", "Double oven", "Self-clean",
            "Griddle", "Induction cooktop", "Smart control"
        ],
        "Microwave": [
            "ADA compliance", "Sensor cooking", "Convection option", "Over-the-range",
            "Built-in", "Child lock", "Quick reheat"
        ],
        "Wall Oven": [
            "ADA compliance", "Double oven", "Convection", "Self-cleaning", "Steam bake",
            "WiFi control", "Touchscreen"
        ],
        "Cooktop": [
            "ADA compliance", "Induction", "Gas", "Electric coil", "Bridge element",
            "Knob or touch controls", "Power boil"
        ],
        "Freezer": [
            "ADA compliance", "Upright", "Chest", "Frost-free", "Garage ready",
            "Temperature alarm", "LED lighting"
        ],
        "Air Conditioner": [
            "ADA compliance", "Portable", "Window-mounted", "Dehumidifier mode",
            "Smart thermostat", "Energy saver", "Remote control"
        ],
        "Wine Cooler": [
            "ADA compliance", "Dual zone", "Built-in or freestanding", "UV protection",
            "Humidity control", "Quiet compressor"
        ],
        "Icemaker": [
            "ADA compliance", "Built-in", "Freestanding", "Clear cube ice",
            "Daily production rate", "Storage capacity"
        ],
        "Laundry Center / Combo": [
            "ADA compliance", "Stackable", "All-in-one", "Steam wash",
            "Sensor dry", "WiFi connectivity", "Space-saving design"
        ],
        "Trash Compactor": [
            "ADA compliance", "Touch-toe drawer", "Odor control", "Air filter",
            "Stainless steel construction", "Removable key lock"
        ],
        "Garbage Disposal": [
            "ADA compliance", "Continuous feed", "Batch feed", "Stainless steel grind components",
            "Sound insulation", "Septic safe"
        ]
    }

    detected_type = "Refrigerator"  # default fallback
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
    feature_check = generate_comparison_table(competitor_info, ge_match, selected_features)
    st.markdown(feature_check, unsafe_allow_html=True)

    show_diff = st.radio("Show what doesn't match?", ["No", "Yes"], horizontal=True)
    if show_diff == "Yes":
        st.subheader("What Doesn't Match")
        diff_table = generate_differences_table()
        st.markdown(diff_table, unsafe_allow_html=True)
