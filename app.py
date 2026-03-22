import pickle
import pandas as pd
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Property Advisor",
    page_icon="🏡",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("cleaned_df.csv")

df = load_data()

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    with open("RF_model.pkl", "rb") as file:
        return pickle.load(file)

model = load_model()

# ---------------- ENCODING FUNCTION ----------------
def get_encoded_loc(location):
    row = df[df["location"] == location]
    if not row.empty:
        return row["encoded_loc"].values[0]
    return None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🏡 Smart Property Advisor")
    st.image(
    "https://images.unsplash.com/photo-1560518883-ce09059eeffa", use_container_width=True)

    page = st.radio("Navigation", [
        "🏠 Home",
        "💰 Price Predictor",
        "📊 Market Dashboard",
        "🏘️ Property Explorer",
        "📅 Book Meeting",
        "📥 Download Report"
    ])

# ---------------- HOME PAGE ----------------
if page == "🏠 Home":
    st.title("🏡 Smart Property Advisor")
    st.markdown("### Find, compare and predict house prices easily")

    st.image("https://images.unsplash.com/photo-1560518883-ce09059eeffa", use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Properties Listed", "1200+")
    col2.metric("Locations Covered", "25+")
    col3.metric("Avg Price Growth", "8.5%")

    st.markdown("---")
    st.info("Use the sidebar to explore features.")

# ---------------- PRICE PREDICTOR ----------------
elif page == "💰 Price Predictor":
    st.title("💰 House Price Prediction")

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            location = st.selectbox("📍 Location", df["location"].unique())
            sqft = st.slider("📐 Area (sqft)", 300, 5000, 1000)

        with col2:
            bath = st.selectbox("🛁 Bathrooms", sorted(df["bath"].unique()))
            bhk = st.selectbox("🏠 BHK", sorted(df["bhk"].unique()))

    if st.button("🔍 Predict Price"):
        encoded_loc = get_encoded_loc(location)

        if encoded_loc is None:
            st.error("Location encoding not found!")
        else:
            with st.spinner("Predicting..."):
                inp_data = [[sqft, bath, bhk, encoded_loc]]
                pred = model.predict(inp_data)[0]

                price = pred * 100000

                st.success("Prediction Complete!")
                st.metric("Estimated Price", f"₹ {price:,.0f}")

                # Save for report
                st.session_state["last_prediction"] = {
                    "location": location,
                    "sqft": sqft,
                    "bath": bath,
                    "bhk": bhk,
                    "price": price
                }

# ---------------- DASHBOARD ----------------
elif page == "📊 Market Dashboard":
    st.title("📊 Market Insights Dashboard")

    # 🔹 Location Filter
    selected_locations = st.multiselect(
        "📍 Select Locations",
        df["location"].unique(),
        default=df["location"].unique()[:3]
    )

    filtered_df = df[df["location"].isin(selected_locations)].copy()

    # 🔹 Row 1 → BHK Insight
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏠 Avg Price by BHK")
        bhk_price = filtered_df.groupby("bhk")["price"].mean()
        st.bar_chart(bhk_price)

    with col2:
        st.subheader("📍 Property Count by Location")
        st.bar_chart(filtered_df["location"].value_counts())

    # 🔹 Row 2 → Price Category
    st.subheader("🏷️ Price Categories")

    def price_category(p):
        if p < 50:
            return "Budget"
        elif p < 100:
            return "Mid-range"
        else:
            return "Premium"

    filtered_df["price_category"] = filtered_df["price"].apply(price_category)

    st.bar_chart(filtered_df["price_category"].value_counts())
# ---------------- PROPERTY EXPLORER ----------------
elif page == "🏘️ Property Explorer":
    st.title("🏘️ Explore Properties")

    # 🔹 Filters
    col1, col2 = st.columns(2)

    with col1:
        selected_location = st.selectbox(
            "📍 Select Location",
            df["location"].unique()
        )

    with col2:
        selected_bhk = st.selectbox(
            "🏠 Select BHK",
            sorted(df["bhk"].unique())
        )

    # 🔹 Filter dataset
    filtered_df = df[
        (df["location"] == selected_location) &
        (df["bhk"] == selected_bhk)
    ].copy()

    # 🔹 Create property table
    properties = filtered_df[["location", "price", "bhk"]].copy()

    # Add fake dealer (you can improve later)
    import random
    dealers = ["ABC Realty", "XYZ Homes", "Prime Estates", "Urban Living", "Dream Homes"]
    properties["Dealer"] = [random.choice(dealers) for _ in range(len(properties))]

    # Rename columns for UI
    properties.columns = ["Location", "Price (Lakh)", "BHK", "Dealer"]

    # 🔹 Show table
    st.dataframe(properties.head(20), use_container_width=True)

    # 🔹 Selection
    if not properties.empty:
        selected_property = st.selectbox(
            "🏡 Select Property",
            properties.index
        )

        selected_row = properties.loc[selected_property]

        st.success("Property Details")
        st.write(selected_row)
    else:
        st.warning("No properties found for selected filters")

# ---------------- BOOK MEETING ----------------
elif page == "📅 Book Meeting":
    st.title("📅 Schedule a Property Visit")

    name = st.text_input("👤 Your Name",placeholder="Enter your full name")
    phone = st.text_input("📱 Mobile Number",placeholder="Enter 10-digit mobile number")

    date = st.date_input("📅 Select Date")
    time = st.time_input("⏰ Select Time")

    dealer = st.selectbox("🏢 Choose Dealer", ["ABC Realty", "XYZ Homes", "Prime Estates"])


        # 🔹 Validation function
    def is_valid_phone(phone):
        return phone.isdigit() and len(phone) == 10

    # 🔹 Button
    if st.button("📌 Book Appointment"):
        if not name:
            st.warning("Please enter your name")

        elif not is_valid_phone(phone):
            st.error("Enter a valid 10-digit mobile number")

        else:
            st.success("✅ Meeting Scheduled Successfully!")
            st.info(f"📞 Dealer {dealer} will contact you soon")
            st.info("Have a nice day ☺️")

# ---------------- DOWNLOAD REPORT ----------------
elif page == "📥 Download Report":
    st.title("📥 Download Property Report")

    if "last_prediction" in st.session_state:
        data = st.session_state["last_prediction"]

        report = f"""
PROPERTY REPORT

Location: {data['location']}
Area: {data['sqft']} sqft
Bathrooms: {data['bath']}
BHK: {data['bhk']}
Estimated Price: ₹ {data['price']:,.0f}
"""

        st.download_button(
            label="📄 Download Report",
            data=report,
            file_name="property_report.txt"
        )

        st.success("Report Ready!")
    else:
        st.warning("Please make a prediction first.")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("© 2026 Smart Property Advisor | Built using Streamlit")