import streamlit as st
import matplotlib
import pandas as pd
from pathlib import Path
from PIL import Image
import base64

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

BASE_DIR = Path(__file__).parent
def to_base64(code):
    path = BASE_DIR / "data" / "flags" / f"{code}.png"
    return base64.b64encode(path.read_bytes()).decode()

def as_data_uri(code):
    b64 = to_base64(code)
    return f"data:image/png;base64,{b64}"

standings = pd.read_feather('data/standings.ftr').rename(columns={' ':'Flag'})
selected_standings = pd.read_feather('data/selected_standings.ftr').rename(columns={' ':'Flag'})

fmt_dict = {'Points': '{:.0f}', 'Max': '{:.0f}', 'Projected': '{:.1f}','Uniqueness':'{:0.0%}','W':'{:.0f}','D':'{:.0f}','L':'{:.0f}',
            'GF':'{:.0f}','GA':'{:.0f}','Points':'{:.0f}','1st':'{:0.0%}','2nd':'{:0.0%}','3rd':'{:0.0%}','4th':'{:0.0%}',
            '32':'{:0.0%}','16':'{:0.0%}','QF':'{:0.0%}','SF':'{:0.0%}','Final':'{:0.0%}','Win':'{:0.0%}'}


tab_fantasy, tab_tournament, tab_selections = st.tabs([f"🏆 Fantasy Results", "Team Results","Selections"])

with tab_fantasy:
    col1, col2, col3 = st.columns([0.6,1,1.025])
    with col1:
        st.markdown("### Standings")
        player_standings = selected_standings.groupby('Person').agg({'Points':'sum','PPR':'sum','Proj':'sum','Uniqueness':'mean'}).sort_values(
            ['Points','Proj'],ascending=False).rename(columns={'PPR':'Max','Proj':'Projected'}).reset_index()
        st.dataframe(player_standings.style.format(fmt_dict).background_gradient(cmap='RdYlGn', subset=['Points']), 
                        hide_index=True, use_container_width=True, height=550)
        
    with col2:
        st.markdown("### Standings - Detail")
        ordered_managers = player_standings['Person'].tolist()
        for i, manager in enumerate(ordered_managers):
            player_detail = selected_standings[selected_standings.Person == manager][['Flag','Country','Short','Group','Points','PPR','Proj','Uniqueness']].rename(
                columns={'PPR':'Max','Proj':'Projected'})
            player_detail.Uniqueness *= 100
            player_detail["Flag"] = player_detail["Short"].apply(as_data_uri)
            pts_val = selected_standings[selected_standings.Person == manager].Points.sum()
            proj_val = selected_standings[selected_standings.Person == manager].Proj.sum()
            leader_icon = "🥇 " if i == 0 else "🥈 " if i == 1 else "🥉 " if i == 2 else ""
            column_config = {"Flag": st.column_config.ImageColumn("Flag")}
            for col, fmt in fmt_dict.items():
                if fmt == "{:.0f}":
                    column_config[col] = st.column_config.NumberColumn(col,format="%.0f")
                elif fmt == "{:.1f}":
                    column_config[col] = st.column_config.NumberColumn(col,format="%.1f")
                elif fmt == "{:0.1%}":
                    column_config[col] = st.column_config.NumberColumn(col,format="%.1f%%")
                elif fmt == "{:0.0%}":
                    column_config[col] = st.column_config.NumberColumn(col,format="%.0f%%")

            with st.expander(f"{leader_icon}{manager} | {pts_val:.0f} points | {proj_val:.1f} projected", expanded=False):
                st.dataframe(player_detail.drop(columns='Short'), use_container_width=True, hide_index=True,column_config=column_config)

    with col3:
        st.markdown('### Standings Over Time')
        player_over_time = selected_standings[['Person', 'PointsbyMatch']]
        player_over_time = player_over_time.join(pd.DataFrame(player_over_time['PointsbyMatch'].tolist(),index=player_over_time.index))
        player_over_time = player_over_time.groupby('Person').sum(numeric_only=True).cumsum(axis=1)
        st.line_chart(player_over_time,height=250,use_container_width=True)

        st.markdown("### Top Teams")
        top_teams = standings.sort_values(['Points','Proj'],ascending=False)[['Flag','Country','Short','Group','Points','PPR','Proj','W','D','L','GD']].rename(
            columns={'PPR':'Max','Proj':'Projected'})
        top_teams["Flag"] = top_teams["Short"].apply(as_data_uri)
        st.container()
        st.dataframe(top_teams.drop(columns='Short'), height=250, hide_index=True,column_config=column_config,use_container_width=False,width = "content")

with tab_tournament:
    col1, col2 = st.columns([1.35,1])
    with col1:
        st.markdown("### Group Stage")
        ordered_groups = ['A','B','C','D','E','F','G','H','I','J','K','L']
        for i, group in enumerate(ordered_groups):
            team_detail = standings[standings.Group == group][['Flag','Country','Short','W','D','L','GF','GA','GD','Points','Proj','1st','2nd','3rd','4th'
                                                               ]].sort_values(['Points','GD','GF','Proj'],ascending=False).rename(columns={'Proj':'Projected'})
            team_detail["Flag"] = team_detail["Short"].apply(as_data_uri)
            team_detail['1st'] *= 100
            team_detail['2nd'] *= 100
            team_detail['3rd'] *= 100
            team_detail['4th'] *= 100
            with st.expander(f"{group}",expanded=False):
                st.dataframe(team_detail.drop(columns='Short').style.background_gradient(cmap='RdYlGn', subset=['1st', '2nd', '3rd', '4th'], vmin=0, vmax=100),
                              use_container_width=True, hide_index=True,column_config=column_config)
    with col2:
        st.markdown("### Knockouts")
        knockout_detail = standings[['Flag','Country','Short','PPR','Proj','32','16','QF','SF','Final','Win']].sort_values('Proj',ascending=False).rename(
            columns={'Proj':'Projected','PPR':'Max'})
        knockout_detail["Flag"] = knockout_detail["Short"].apply(as_data_uri)
        knockout_detail['32'] *= 100
        knockout_detail['16'] *= 100
        knockout_detail['QF'] *= 100
        knockout_detail['SF'] *= 100
        knockout_detail['Final'] *= 100
        knockout_detail['Win'] *= 100
        st.dataframe(knockout_detail.drop(columns='Short').style.background_gradient(cmap='RdYlGn', subset=['32', '16', 'QF', 'SF','Final','Win'], vmin=0, vmax=100),
                              use_container_width=True, hide_index=True,column_config=column_config)
        
with tab_selections:
    st.markdown('## Coming soon')