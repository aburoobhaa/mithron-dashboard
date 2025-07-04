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
st.set_page_config(page_title="MITHRON DASHBOARD", layout="wide")

#--------------------------
#logo 
# -----------------------
logo_path = os.path.join("assets", "logo2.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as image_file:
        encoded_logo = base64.b64encode(image_file.read()).decode()
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="data:image/png;base64,{encoded_logo}" width="140" />
                <h3 style="margin-top: 10px; margin-bottom: 0; color: #FFA500;">MITHRON</h3>
            </div>
        """, unsafe_allow_html=True)
# -------------------------------
# 🍗 Theme Switch
# -------------------------------
theme_mode = st.sidebar.radio("Theme Mode", ["Light", "Dark"])
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
full_month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

month_to_index = {m: i for i, m in enumerate(month_order)}
index_to_month = {i: m for i, m in enumerate(month_order)}
full_month_to_index = {m: i for i, m in enumerate(full_month_order)}
index_to_full_month = {i: m for i, m in enumerate(full_month_order)}

current_month = datetime.now().strftime("%b")
next_month = month_order[(month_order.index(current_month) + 1) % 12]
current_month_full = datetime.now().strftime("%B")
next_month_full = full_month_order[(full_month_order.index(current_month_full) + 1) % 12]

highlight_months = [current_month, next_month]
highlight_months_full = [current_month_full, next_month_full]

# Seasonal mapping
season_to_months = {
    "Autumn": ["Oct", "Nov"],
    "Summer": ["Mar", "Apr", "May"],
    "Winter": ["Nov", "Dec", "Jan", "Feb"],
    "Monsoon": ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov"],
    "Annual": month_order,
    "Perennial": month_order
}

season_to_full_months = {
    "Autumn": ["October", "November"],
    "Summer": ["March", "April", "May"],
    "Winter": ["November", "December", "January", "February"],
    "Monsoon": ["June", "July", "August", "September", "October", "November"],
    "Annual": full_month_order,
    "Perennial": full_month_order
}

def expand_seasons(month_field):
    if pd.isna(month_field) or month_field == "":
        return ""
    parts = [s.strip() for s in str(month_field).split(',') if s.strip()]
    months = []
    for part in parts:
        # Handle both abbreviated and full month names
        if part in season_to_months:
            months.extend(season_to_months[part])
        elif part in season_to_full_months:
            months.extend(season_to_full_months[part])
        elif part in month_order:
            months.append(part)
        elif part in full_month_order:
            months.append(part)
    return ', '.join(sorted(set(months), key=lambda m: full_month_order.index(m) if m in full_month_order else month_order.index(m)))

def add_month_delay(months, delay):
    if not months or pd.isna(months):
        return ""
    out_months = []
    for m in expand_seasons(months).split(','):
        m = m.strip()
        if m in month_to_index:
            new_idx = (month_to_index[m] + delay) % 12
            out_months.append(index_to_month[new_idx])
        elif m in full_month_to_index:
            new_idx = (full_month_to_index[m] + delay) % 12
            out_months.append(index_to_full_month[new_idx])
    return ', '.join(out_months)

def explode_months(df, col):
    rows = []
    for _, row in df.iterrows():
        months = str(row[col]) if pd.notna(row[col]) else ""
        for m in months.split(','):
            m = m.strip()
            if m:
                r = row.copy()
                r[col] = m
                rows.append(r)
    return pd.DataFrame(rows)

# -------------------------------
# State Selection + File Load
# -------------------------------
available_states = ["Tamil Nadu", "Kerala", "Andhra Pradesh", "Karnataka"]
state_selected = st.sidebar.selectbox("🕜️ Select State", available_states, index=0)

# csv_paths = {
 #   "Tamil Nadu": r"C:\Users\Aburoobha\OneDrive\Desktop\PROJECT\MITHRON\ALL_EXCEL\New folder\DASHBOARD\data\Tamilnadu.csv",
  #  "Kerala": r"C:\Users\Aburoobha\OneDrive\Desktop\PROJECT\MITHRON\ALL_EXCEL\New folder\DASHBOARD\data\Kerala.csv",
   # "Andhra Pradesh": r"C:\Users\Aburoobha\OneDrive\Desktop\PROJECT\MITHRON\ALL_EXCEL\New folder\DASHBOARD\data\Andhra.csv",
    #"Karnataka": r"C:\Users\Aburoobha\OneDrive\Desktop\PROJECT\MITHRON\ALL_EXCEL\New folder\DASHBOARD\data\Karnataka.csv"
#} '''


csv_paths = {
    "Tamil Nadu": os.path.join("data", "Tamilnadu.csv"),
    "Kerala": os.path.join("data", "Kerala.csv"),
    "Andhra Pradesh": os.path.join("data", "Andhra.csv"),
    "Karnataka": os.path.join("data", "Karnataka.csv")
}

csv_path = csv_paths[state_selected]

try:
    if not csv_path or not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset for {state_selected} not found at: {csv_path}")

    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, encoding='ISO-8859-1')

    #st.sidebar.success(f"Loaded file for {state_selected}: `{csv_path}`")
except Exception as e:
    st.error(f"Failed to load dataset for {state_selected}: {e}")
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
#logo_path = r"assets\logo2.png"
logo_path = os.path.join("assets", "logo2.png")
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

# Determine which month format to use based on state
use_full_months = state_selected in ["Andhra Pradesh", "Karnataka"]
month_selection = full_month_order if use_full_months else month_order

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    selected_crops = st.multiselect("🌾 Crop", sorted(df['CROP'].unique()), default=sorted(df['CROP'].unique()), label_visibility="visible")
with col2:
    selected_districts = st.multiselect("🏩 District", sorted(df['DISTRICT'].unique()), default=sorted(df['DISTRICT'].unique()), label_visibility="visible")
with col3:
    selected_months = st.multiselect("📅 Sowing Month", month_selection, default=month_selection)

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
# 🔍 Apply Filters (with empty filter handling)
# -------------------------------
if not selected_crops:
    selected_crops = sorted(df['CROP'].unique())
if not selected_districts:
    selected_districts = sorted(df['DISTRICT'].unique())
if not selected_months:
    selected_months = month_selection

filtered = df[
    df['CROP'].isin(selected_crops) &
    df['DISTRICT'].isin(selected_districts) &
    df['MONTH'].apply(lambda x: any(m in expand_seasons(x) for m in selected_months) if pd.notna(x) else False)
].copy()

# -------------------------------
# 💭 Spray Suggestions (with null handling)
# -------------------------------
filtered['Suggested Spray Month'] = filtered.apply(
    lambda row: add_month_delay(row['MONTH'], spray_delay_map[row['CROP']]) if pd.notna(row['MONTH']) else "", 
    axis=1
)
filtered['Manual Spray Month'] = ""

# -------------------------------
# ☔️ Rainy Season Logic
# -------------------------------
# Define rainy seasons for each state
kerala_rain = {d: ["June", "July", "August", "September"] for d in [
    "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Alappuzha", "Kottayam", "Idukki",
    "Ernakulam", "Thrissur", "Palakkad", "Malappuram", "Kozhikode", "Wayanad",
    "Kannur", "Kasaragod"]}

tn_rain = {
    "Chennai": ["October", "November", "December"],
    "Coimbatore": ["July", "August", "September"],
    "Madurai": ["October", "November"],
    "Tiruchirappalli": ["September", "October", "November"],
    "Salem": ["September", "October"]
}

andhra_rain = {d: ["June", "July", "August", "September"] for d in [
    "Alluri sitharama raju", "Anakapalli", "Anantapur", "Annamayya", "Bapatla", 
    "Chittoor", "East godavari", "Eluru", "Guntur", "Kadapa", "Kakinada", 
    "Konaseema", "Krishna", "Kurnool", "Nandyal", "Ntr", "Palnadu", 
    "Parvathipuram manyam", "Prakasam", "Spsr nellore", "Sri sathya sai", 
    "Srikakulam", "Tirupati", "Visakhapatanam", "Vizianagaram", "West godavari"]}

karnataka_rain = {d: ["June", "July", "August", "September"] for d in [
    "Bangalore", "Chikmangaluru", "Davangere", "Gulbarga", "Hassan", 
    "Kasaragodu", "Kodagu", "Madikeri", "Mangalore", "Mysuru", "Raichur"]}

# Select the appropriate rainy season data
rain_data = {
    "Tamil Nadu": tn_rain,
    "Kerala": kerala_rain,
    "Andhra Pradesh": andhra_rain,
    "Karnataka": karnataka_rain
}[state_selected]

def get_rainy_match(row):
    spray_months = [m.strip() for m in str(row['Suggested Spray Month']).split(',') if m.strip()]
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
    column_config={
        "Manual Spray Month": st.column_config.TextColumn(
            help="Override spray month manually (use same format as original data)"
        )
    },
    use_container_width=True,
    hide_index=True
)

# -------------------------------
# 📊 Visualizations
# -------------------------------
def get_rainy_match_count(row):
    spray_months = set(str(row['Suggested Spray Month']).split(', ')) if pd.notna(row['Suggested Spray Month']) else set()
    rainy_months = set(str(row.get('Rainy Season', '')).split(', ')) if pd.notna(row.get('Rainy Season', '')) else set()
    if "No Possibility" in rainy_months:
        return 0
    return len(spray_months & rainy_months)

def render_visualizations(filtered, state_selected, month_order):
    st.subheader("📊 Optimized Analytics")

    # Determine if we're using full month names
    use_full_months = state_selected in ["Andhra Pradesh", "Karnataka"]
    display_month_order = full_month_order if use_full_months else month_order
    
    # 1. Scatter Plot: Crop Spray by Month and District
    st.subheader("🌾 Scatter Plot – Crops by Spray Month and District")
    spray_crop_data = explode_months(filtered, 'Suggested Spray Month')
    if not spray_crop_data.empty:
        spray_crop_data['Bubble Size'] = 0.5
        spray_crop_data['Suggested Spray Month'] = pd.Categorical(
            spray_crop_data['Suggested Spray Month'], categories=display_month_order, ordered=True
        )

        fig_scatter_crop = px.scatter(
            spray_crop_data,
            x='Suggested Spray Month',
            y='DISTRICT',
            color='CROP',
            size='Bubble Size',
            hover_data=['CROP', 'DISTRICT', 'Suggested Spray Month'],
            title="🌾 Crop Variety Spray Plan by District & Month",
            size_max=7,
            opacity=1,
            height=700
        )
        fig_scatter_crop.update_traces(marker=dict(line=dict(width=0.9, color='black')))
        fig_scatter_crop.update_layout(xaxis_title="Spray Month", yaxis_title="District", plot_bgcolor="#fff")
        st.plotly_chart(fig_scatter_crop, use_container_width=True)
    else:
        st.warning("No data available for visualization")

    # 2. Line Chart – Crop Frequency by Month
    crop_month = explode_months(filtered, 'MONTH')
    if not crop_month.empty:
        line1 = crop_month.groupby(['MONTH', 'CROP']).size().reset_index(name='Count')
        line1['MONTH'] = pd.Categorical(line1['MONTH'], categories=display_month_order, ordered=True)
        line1 = line1.sort_values('MONTH')

        fig_crop_to_month = px.line(
            line1,
            x='MONTH',
            y='Count',
            color='CROP',
            markers=True,
            title="🌾 Crop Frequency by Sowing Month"
        )
        st.plotly_chart(fig_crop_to_month, use_container_width=True)
    else:
        st.warning("No data available for crop frequency visualization")

    # 3. Colored scatter plot
    scatter_data = explode_months(filtered, 'Suggested Spray Month')[
        ['DISTRICT', 'CROP', 'Suggested Spray Month']
    ].drop_duplicates()
    if not scatter_data.empty:
        vedantu_colors = [
            "#F78F1E", "#FFD400", "#EC007B", "#0047AB", "#0071BC", "#A3D977",
            "#FF69B4", "#00CED1", "#8A2BE2", "#32CD32", "#DC143C", "#20B2AA"
        ]
        scatter_data['Suggested Spray Month'] = pd.Categorical(
            scatter_data['Suggested Spray Month'], categories=display_month_order, ordered=True
        )

        fig_custom_color = px.scatter(
            scatter_data,
            x='CROP',
            y='DISTRICT',
            color='Suggested Spray Month',
            color_discrete_sequence=vedantu_colors,
            title='🗓️ Crop Appearance by District (Vedantu Style Colors by Month)',
            height=800
        )
        fig_custom_color.update_traces(marker=dict(size=10, opacity=0.7, line=dict(width=1, color='black')))
        st.plotly_chart(fig_custom_color, use_container_width=True)
    else:
        st.warning("No data available for colored scatter plot")

    # 4. Donut Pie Chart: Distribution by User Selection
    st.subheader("🍩 Distribution Insights (Smooth Donut Style)")
    donut_option = st.selectbox("View Proportions By", ["📅 Sowing Month", "🌾 Crop", "🏙️ District"])
    group_col = {"📅 Sowing Month": 'MONTH', "🌾 Crop": 'CROP', "🏙️ District": 'DISTRICT'}[donut_option]

    donut_data = explode_months(filtered, group_col) if group_col == 'MONTH' else filtered.copy()
    if not donut_data.empty:
        donut_summary = donut_data[group_col].value_counts().reset_index()
        donut_summary.columns = [group_col, 'Count']

        fig_donut = px.pie(
            donut_summary,
            names=group_col,
            values='Count',
            hole=0.45,
            title=f"🍩 {donut_option} Distribution Overview",
            color_discrete_sequence=px.colors.sequential.Plasma_r
        )
        fig_donut.update_traces(
            textposition='inside', textinfo='percent+label',
            marker=dict(line=dict(color='#ffffff', width=2)),
            pull=[0.02] * len(donut_summary)
        )
        fig_donut.update_layout(
            annotations=[dict(text=group_col, x=0.5, y=0.5, font_size=18, showarrow=False)]
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.warning("No data available for donut chart")

    # 5. Horizontal Bar Chart: Sowing Month Count per District
    month_dist = explode_months(filtered, 'MONTH')
    if not month_dist.empty:
        bar1 = month_dist.groupby(['DISTRICT'])['MONTH'].nunique().reset_index()
        bar1.columns = ['DISTRICT', 'SOWING MONTH COUNT']

        fig_month_to_district = px.bar(
            bar1,
            x='SOWING MONTH COUNT',
            y='DISTRICT',
            orientation='h',
            title='📅 Sowing Month Count per District',
            text_auto=True
        )
        st.plotly_chart(fig_month_to_district, use_container_width=True)
    else:
        st.warning("No data available for horizontal bar chart")

    # 6. Radar Chart
    st.subheader("🕸️ Radar Chart – Sowing vs Suggested Spray by Crop (Top 10)")
    sow_exp = explode_months(filtered.copy(), 'MONTH')
    spray_exp = explode_months(filtered.copy(), 'Suggested Spray Month')
    
    if not sow_exp.empty and not spray_exp.empty:
        sow_count = sow_exp.groupby('CROP')['MONTH'].nunique().reset_index(name='Sowing Months')
        spray_count = spray_exp.groupby('CROP')['Suggested Spray Month'].nunique().reset_index(name='Suggested Spray Months')

        radar_df = pd.merge(sow_count, spray_count, on='CROP', how='inner')
        radar_df['Max'] = radar_df[['Sowing Months', 'Suggested Spray Months']].max(axis=1)
        radar_df = radar_df.sort_values(by='Max', ascending=False).head(10).drop(columns='Max')

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=radar_df['Sowing Months'],
            theta=radar_df['CROP'],
            fill='toself',
            name='Sowing',
            line_color='rgba(148, 0, 211, 0.9)',
            fillcolor='rgba(186, 85, 211, 0.3)'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=radar_df['Suggested Spray Months'],
            theta=radar_df['CROP'],
            fill='toself',
            name='Suggested Spray',
            line_color='rgba(255, 105, 180, 0.9)',
            fillcolor='rgba(255, 182, 193, 0.3)'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max(radar_df[['Sowing Months', 'Suggested Spray Months']].max()) + 1])),
            showlegend=True,
            title="🕸️ Radar Chart – Crop Month Spread (Pink/Violet Theme)",
            height=600
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.warning("No data available for radar chart")

    # 7. Rainy Match Bar & Donut Charts
    match_df = filtered.copy()
    if not match_df.empty:
        match_df['Rainy Match Count'] = match_df.apply(get_rainy_match_count, axis=1)
        match_df['Has Match'] = match_df['Rainy Match Count'].apply(lambda x: 'Match' if x > 0 else 'No Match')

        district_match = match_df.groupby('DISTRICT')['Rainy Match Count'].sum().reset_index()
        fig_district_match = px.bar(
            district_match,
            x='DISTRICT',
            y='Rainy Match Count',
            title="🌧️ Rainy Month Match Count per District",
            text_auto=True
        )
        st.plotly_chart(fig_district_match, use_container_width=True)

        crop_summary = match_df.groupby(['CROP', 'Has Match']).size().reset_index(name='Count')
        green_shades = px.colors.sequential.Greens[len(crop_summary):] + px.colors.sequential.Greens[:len(crop_summary)]

        fig_donut = px.pie(
            crop_summary,
            names='CROP',
            values='Count',
            color='CROP',
            title="🌿 Crop-wise Suggested Spray Match with Rainy Season",
            hole=0.4,
            color_discrete_sequence=green_shades
        )
        fig_donut.update_traces(
            textposition='outside',
            textinfo='label+percent',
            marker=dict(line=dict(color='#ffffff', width=2))
        )
        fig_donut.update_layout(annotations=[dict(text="Crops", x=0.5, y=0.5, font_size=18, showarrow=False)])
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.warning("No data available for rainy season analysis")

render_visualizations(filtered, state_selected, month_selection)

# -------------------------------
# 🗵️ Download Button
# -------------------------------
st.download_button(
    label="⬇️ Download Spray Plan CSV",
    data=edited_df.to_csv(index=False),
    file_name="spray_plan.csv",
    mime="text/csv"
)


    

