import streamlit as st
import matplotlib
import pandas as pd

# --- 1. CONFIG & COMPACT STYLING ---
st.set_page_config(layout="wide", page_title="World Cup Fantasy")

# CUSTOM CSS: Shrinks headers, table padding, and overall container gaps
st.markdown("""
    <style>
    /* Reduce top/side margins */
    .block-container {padding-top: 2.8rem; padding-bottom: 2rem; padding-left: 1rem; padding-right: 2rem;}
            
    /* Shrinks the expander header text and reduces the vertical padding */
            .streamlit-expanderHeader {
            font-size: 12px !important;
            padding-top: 1px !important;
            padding-bottom: 1px !important;
    }
            
    /* Shrink Header sizes */
    h1 { font-size: 14px !important; margin-bottom: 0.2rem !important; }
    h3 { font-size: 14px !important; margin-top: 0.2rem !important; margin-bottom: 0.2rem !important; }
    
    /* Global font size for Dataframes */
    .stDataFrame div { font-size: 10px !important; }
    
    /* Condense Expander headers */
    div[data-testid="stExpander"] div[role="button"] p { font-size: 12px !important; font-weight: bold; }
    
    /* Reduce gap between elements */
    [data-testid="stVerticalBlock"] { gap: 0.2rem !important; }
    </style>
    """, unsafe_allow_html=True)


standings = pd.read_feather('data/standings.ftr')
selected_standings = pd.read_feather('data/selected_standings.ftr')

fmt_dict = {'Points': '{:.0f}', 'Max': '{:.0f}', 'Projected': '{:.1f}','Uniqueness':'{:0.1%}','W':'{:.0f}','D':'{:.0f}','L':'{:.0f}',
            'GF':'{:.0f}','GA':'{:.0f}','Points':'{:.0f}','1st':'{:0.2%}','2nd':'{:0.2%}','3rd':'{:0.2%}','4th':'{:0.2%}'}


tab_fantasy, tab_tournament, tab_selections = st.tabs([f"🏆 Fantasy Results", "Team Results","Selections"])

with tab_fantasy:
    col1, col2, col3 = st.columns([2/3,1,1])
    with col1:
        st.markdown("### Standings")
        player_standings = selected_standings.groupby('Person').agg({'Points':'sum','PPR':'sum','Proj':'sum','Uniqueness':'mean'}).sort_values(
            ['Points','Proj'],ascending=False).rename(columns={'PPR':'Max','Proj':'Projected'}).reset_index()
        st.dataframe(player_standings.style.format(fmt_dict).background_gradient(cmap='RdYlGn', subset=['Points']), 
                        hide_index=True, use_container_width=True, height=480)
        
    with col2:
        st.markdown("### Standings - Detail")
        ordered_managers = player_standings['Person'].tolist()
        for i, manager in enumerate(ordered_managers):
            player_detail = selected_standings[selected_standings.Person == manager][[' ','Country','Short','Group','Points','PPR','Proj','Uniqueness']].rename(
                columns={'PPR':'Max','Proj':'Projected'})
            player_detail[" "] = player_detail["Short"].apply(lambda x: f"data/flags/{x}.png")
            pts_val = selected_standings[selected_standings.Person == manager].Points.sum()
            proj_val = selected_standings[selected_standings.Person == manager].Proj.sum()
            leader_icon = "🥇 " if i == 0 else "🥈 " if i == 1 else "🥉 " if i == 2 else ""
            column_config = {" ": st.column_config.ImageColumn(" ",help="Country flag")}
            for col, fmt in fmt_dict.items():
                if fmt == "{:.0f}":
                    column_config[col] = st.column_config.NumberColumn(col,format="%.0f")
                elif fmt == "{:.1f}":
                    column_config[col] = st.column_config.NumberColumn(col,format="%.1f")
                elif fmt == "{:0.1%}":
                    column_config[col] = st.column_config.NumberColumn(col,format="%.1f%%")
                elif fmt == "{:0.2%}":
                    column_config[col] = st.column_config.NumberColumn(col,format="%.2f%%")

            with st.expander(f"{leader_icon}{manager} | {pts_val:.0f} points | {proj_val:.1f} projected", expanded=False):
                st.dataframe(player_detail.drop(columns='Short'), use_container_width=False, hide_index=True,width = "content",column_config=column_config)

    with col3:
        st.markdown('### Standings Over Time')
        st.markdown('To come')

        st.markdown("### Top Teams")
        top_teams = standings.sort_values(['Points','Proj'],ascending=False)[[' ','Country','Short','Group','Points','PPR','Proj','W','D','L','GD']].rename(
            columns={'PPR':'Max','Proj':'Projected'})
        top_teams[" "] = top_teams["Short"].apply(lambda x: f"data/flags/{x}.png")
        st.dataframe(top_teams.drop(columns='Short'), height=250, use_container_width=True, hide_index=True,width = "content",column_config=column_config)
        st.write(player_detail[" "].head())
        st.image(player_detail[" "].iloc[0])
        st.write(st.__version__)
        st.write(player_detail[" "].head())
        st.write(player_detail[" "].dtype)
        test_df = pd.DataFrame({"Flag": [player_detail[" "].iloc[0]]})
        st.dataframe(test_df,column_config={"Flag": st.column_config.ImageColumn("Flag")})