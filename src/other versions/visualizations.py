import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

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

def get_rainy_match_count(row):
    spray_months = set(row['Suggested Spray Month'].split(', '))
    rainy_months = set(row.get('Rainy Season', '').split(', '))
    if "No Possibility" in rainy_months:
        return 0
    return len(spray_months & rainy_months)

def render_visualizations(filtered, state_selected, month_order):
    st.subheader("📊 Optimized Analytics")

    # 1. Scatter Plot: Crop Spray by Month and District
    st.subheader("🌾 Scatter Plot – Crops by Spray Month and District")
    spray_crop_data = explode_months(filtered, 'Suggested Spray Month')
    spray_crop_data['Bubble Size'] = 0.5
    spray_crop_data['Suggested Spray Month'] = pd.Categorical(
        spray_crop_data['Suggested Spray Month'], categories=month_order, ordered=True
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

    # 2. Line Chart – Crop Frequency by Month (Skip for Kerala)
    if state_selected != "Kerala":
        crop_month = explode_months(filtered, 'MONTH')
        line1 = crop_month.groupby(['MONTH', 'CROP']).size().reset_index(name='Count')
        line1['MONTH'] = pd.Categorical(line1['MONTH'], categories=month_order, ordered=True)
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
        st.info("📉 Crop Frequency Line Chart not available for Kerala.")

    # 3. Colored Scatter Plot – Crop by District by Month (Skip for Tamil Nadu)
    if state_selected != "Tamil Nadu":
        vedantu_colors = [
            "#F78F1E", "#FFD400", "#EC007B", "#0047AB", "#0071BC", "#A3D977",
            "#FF69B4", "#00CED1", "#8A2BE2", "#32CD32", "#DC143C", "#20B2AA"
        ]
        scatter_data = explode_months(filtered, 'Suggested Spray Month')[
            ['DISTRICT', 'CROP', 'Suggested Spray Month']
        ].drop_duplicates()
        scatter_data['Suggested Spray Month'] = pd.Categorical(
            scatter_data['Suggested Spray Month'], categories=month_order, ordered=True
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
        st.info("🎨 Colored Month Scatter Plot not available for Tamil Nadu.")

    # 4. Donut Pie Chart: Distribution by User Selection
    st.subheader("🍩 Distribution Insights (Smooth Donut Style)")
    donut_option = st.selectbox("View Proportions By", ["📅 Sowing Month", "🌾 Crop", "🏙️ District"])
    group_col = {"📅 Sowing Month": 'MONTH', "🌾 Crop": 'CROP', "🏙️ District": 'DISTRICT'}[donut_option]

    donut_data = explode_months(filtered, group_col) if group_col == 'MONTH' else filtered.copy()
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

    # 5. Horizontal Bar Chart: Sowing Month Count per District
    month_dist = explode_months(filtered, 'MONTH')
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

    # 6. Radar Chart – Skip for Tamil Nadu
    if state_selected != "Tamil Nadu":
        st.subheader("🕸️ Radar Chart – Sowing vs Suggested Spray by Crop (Top 10)")
        sow_exp = explode_months(filtered.copy(), 'MONTH')
        spray_exp = explode_months(filtered.copy(), 'Suggested Spray Month')

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
        st.info("🕸️ Radar Chart not available for Tamil Nadu.")

    # 7. Rainy Match Bar & Donut Charts
    match_df = filtered.copy()
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
