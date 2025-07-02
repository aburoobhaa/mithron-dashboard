# -------------------------------
# 🧐 Required Libraries
# -------------------------------
import streamlit as st
import pandas as pd
import base64
import os
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go

# -------------------------------
# ⚙️ Setup Page
# -------------------------------
st.set_page_config(page_title="MITHRON", layout="wide")

# -------------------------------
# 🍗 Theme Switch
# -------------------------------
theme_mode = st.sidebar.radio("🍗 Theme Mode", ["Light", "Dark"])
custom_theme_css = f"""
<style>
    html {{ background-color: {'#fff' if theme_mode == 'Light' else '#0e1117'}; color: {'#000' if theme_mode == 'Light' else '#fafafa'}; }}
    .stApp {{ background-color: {'#fff' if theme_mode == 'Light' else '#0e1117'}; color: {'#000' if theme_mode == 'Light' else '#fafafa'}; }}
    .stMultiSelect label {{ width: 100% !important; }}
</style>
"""
st.markdown(custom_theme_css, unsafe_allow_html=True)

# -------------------------------
# 🗓️ Month Utilities
# -------------------------------
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_to_index = {m: i for i, m in enumerate(month_order)}
index_to_month = {i: m for i, m in enumerate(month_order)}
current_month = datetime.now().strftime("%b")
next_month = month_order[(month_order.index(current_month) + 1) % 12]
highlight_months = [current_month, next_month]

# Seasonal mapping (used to calculate spray months from seasons)
season_to_months = {
    "Autumn": ["Oct", "Nov"],
    "Summer": ["Mar", "Apr", "May"],
    "Winter": ["Nov", "Dec", "Jan", "Feb"],
    "Monsoon": ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov"],
    "Annual": month_order,
    "Perennial": month_order
}

def expand_seasons(month_field):
    parts = [s.strip().capitalize() for s in str(month_field).split(',') if s.strip()]
    months = []
    for part in parts:
        if part in season_to_months:
            months.extend(season_to_months[part])
        elif part in month_order:
            months.append(part)
    return ', '.join(sorted(set(months), key=lambda m: month_order.index(m)))

def add_month_delay(months, delay):
    out_months = []
    for m in expand_seasons(months).split(','):
        m = m.strip()
        if m in month_to_index:
            new_idx = (month_to_index[m] + delay) % 12
            out_months.append(index_to_month[new_idx])
    return ', '.join(out_months)

def explode_months(df, col):
    rows = []
    for _, row in df.iterrows():
        for m in str(row[col]).split(','):
            m = m.strip()
            if m:
                r = row.copy()
                r[col] = m
                rows.append(r)
    return pd.DataFrame(rows)

# -------------------------------
# 📂 State Selection + File Load
# -------------------------------
available_states = ["Tamil Nadu", "Kerala"]
state_selected = st.sidebar.selectbox("🕜️ Select State", available_states, index=0)

csv_paths = {
    "Tamil Nadu": "crop_data.csv",
    "Kerala": "kerala.csv"
}

csv_path = csv_paths[state_selected]

try:
    if not csv_path or not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset for {state_selected} not found at: {csv_path}")

    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding='ISO-8859-1')

    st.sidebar.success(f"✅ Loaded file for {state_selected}: `{csv_path}`")
except Exception as e:
    st.error(f"❌ Failed to load dataset for {state_selected}: {e}")
    st.stop()

# -------------------------------
# 🚱️ Clean Columns
# -------------------------------
df.columns = df.columns.str.strip()
df['MONTH'] = df['MONTH'].astype(str).fillna("").str.replace(r'\s*,\s*', ', ', regex=True).str.strip()
df['CROP'] = df['CROP'].astype(str).fillna("").str.strip()
df['DISTRICT'] = df['DISTRICT'].astype(str).fillna("").str.strip()

# -------------------------------
# 🖐️ Logo
# -------------------------------
logo_path = "logo2.png"
with open(logo_path, "rb") as image_file:
    encoded_logo = base64.b64encode(image_file.read()).decode()

st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; margin-top: -80px;">
        <div style="background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(8px); border-radius: 16px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15); padding: 12px 20px; display: flex; align-items: center;">
            <img src="data:image/png;base64,{encoded_logo}" width="140" style="margin-right: 20px;" />
            <h2 style="margin: 0; font-family: Arial, sans-serif; font-weight: 600; font-size: 25px;">
                <span style="color: #FFA500;">MITHRON</span>
                <span style="color: #000000;"> ADMIN DATA </span>
                <span style="color: #00A86B;">DASHBOARD</span>
            </h2>
        </div>
    </div>
""", unsafe_allow_html=True)

# -------------------------------
# 🔹 Filters
# -------------------------------
st.subheader("Filter Your Data")

filter_style = """
<style>
    div[data-baseweb="select"] > div {
        max-height: 43px !important;
        overflow: hidden;
    }
</style>
"""
st.markdown(filter_style, unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    selected_crops = st.multiselect("🌾 Crop", sorted(df['CROP'].unique()), default=sorted(df['CROP'].unique()), label_visibility="visible")
with col2:
    selected_districts = st.multiselect("🏩 District", sorted(df['DISTRICT'].unique()), default=sorted(df['DISTRICT'].unique()), label_visibility="visible")
with col3:
    selected_months = st.multiselect("📅 Sowing Month", month_order, default=month_order)

# -------------------------------
# ⏱️ Offsets
# -------------------------------
with st.sidebar:
    st.header("⏱️ Crop-wise Offsets (1–12)")
    crop_list = sorted(df['CROP'].unique())
    spray_delay_map = {
        crop: st.number_input(f"{crop}", min_value=1, max_value=12, value=1, step=1, key=f"offset_{crop}")
        for crop in crop_list
    }

# -------------------------------
# 🔍 Apply Filters
# -------------------------------
filtered = df[
    df['CROP'].isin(selected_crops) &
    df['DISTRICT'].isin(selected_districts) &
    df['MONTH'].apply(lambda x: any(m in expand_seasons(x) for m in selected_months) if pd.notnull(x) else False)
].copy()

# -------------------------------
# 💭 Spray Suggestions
# -------------------------------
filtered['Suggested Spray Month'] = filtered.apply(
    lambda row: add_month_delay(row['MONTH'], spray_delay_map[row['CROP']]), axis=1
)
filtered['Manual Spray Month'] = ""

# -------------------------------
# ☔️ Rainy Season Logic
# -------------------------------
kerala_rain = {d: ["Jun", "Jul", "Aug", "Sep"] for d in [
    "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha", "Kottayam", "Idukki",
    "Ernakulam", "Thrissur", "Palakkad", "Malappuram", "Kozhikode", "Wayanad",
    "Kannur", "Kasaragod"]}

tn_rain = {
    "Chennai": ["Oct", "Nov", "Dec"],
    "Coimbatore": ["Jul", "Aug", "Sep"],
    "Madurai": ["Oct", "Nov"],
    "Tiruchirappalli": ["Sep", "Oct", "Nov"],
    "Salem": ["Sep", "Oct"]
}

rain_data = kerala_rain if state_selected == "Kerala" else tn_rain

def get_rainy_match(row):
    spray_months = [m.strip() for m in str(row['Suggested Spray Month']).split(',') if m.strip() in month_order]
    district = row['DISTRICT']
    rainy_months = rain_data.get(district, [])
    matches = [m for m in spray_months if m in rainy_months]
    return ', '.join(matches) if matches else "No Possibility"

filtered['Rainy Season'] = filtered.apply(get_rainy_match, axis=1)

# -------------------------------
# 📊 Editable Table
# -------------------------------
st.subheader("📊 Spray Plan Table (Editable)")
edited_df = st.data_editor(
    filtered,
    column_config={"Manual Spray Month": st.column_config.TextColumn(help="Override spray month manually")},
    use_container_width=True
)

# -------------------------------
# 📊 Visualizations
# -------------------------------
from visualizations import render_visualizations
render_visualizations(filtered, state_selected, month_order)

# -------------------------------
# 🗵️ Download Button
# -------------------------------
st.download_button(
    label="⬇️ Download Spray Plan CSV",
    data=edited_df.to_csv(index=False),
    file_name="spray_plan.csv",
    mime="text/csv"
)  # END
