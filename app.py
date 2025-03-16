import streamlit as st
import pandas as pd
import json
import plotly.express as px

# Title and description
st.title("Football Match Events Dashboard")
st.markdown("This dashboard visualizes events from a football match using the provided event data.")

# Load the JSON file (assumes data.json is in the working directory)
with open("data.json", "r") as f:
    data = json.load(f)

# Extract match info and event data
match_info = data["matchInfo"]
events = data["liveData"]["event"]

# Create a DataFrame from event data
df_events = pd.json_normalize(events)

# Sidebar: show match details
st.sidebar.header("Match Details")
home_team = match_info["contestant"][0]["name"]
away_team = match_info["contestant"][1]["name"]
st.sidebar.write(f"**Match:** {home_team} vs {away_team}")
st.sidebar.write(f"**Date:** {match_info['localDate']}")
st.sidebar.write(f"**Venue:** {match_info['venue']['longName']}")

# Create a mapping for team filtering
team_mapping = {team["name"]: team["id"] for team in match_info["contestant"]}
team_options = ["All"] + list(team_mapping.keys())

# Sidebar filter: select team
selected_team = st.sidebar.selectbox("Filter by Team", options=team_options)

# Sidebar filter: select event types (using typeId; adjust as needed)
unique_types = sorted(df_events["typeId"].unique())
selected_types = st.sidebar.multiselect("Filter by Event Type (typeId)", options=unique_types, default=unique_types)

# Apply filters
df_filtered = df_events.copy()
if selected_team != "All":
    selected_team_id = team_mapping[selected_team]
    df_filtered = df_filtered[df_filtered["contestantId"] == selected_team_id]
df_filtered = df_filtered[df_filtered["typeId"].isin(selected_types)]

# Create a pitch scatter plot using Plotly
fig = px.scatter(
    df_filtered,
    x="x", y="y",
    color="typeId",  # color by event type; you might later map these to descriptive names
    hover_data=["playerName", "timeStamp", "timeMin", "timeSec"],
    title="Event Locations on the Pitch"
)

# Update layout to mimic a football pitch (assuming x and y values range 0-100)
fig.update_layout(
    xaxis=dict(range=[0, 100], title="Pitch Width"),
    yaxis=dict(range=[0, 100], title="Pitch Length", scaleanchor="x", scaleratio=1),
    shapes=[
        # Outer boundary of the pitch
        dict(type="rect", x0=0, y0=0, x1=100, y1=100, line=dict(color="black", width=2)),
        # Center line
        dict(type="line", x0=50, y0=0, x1=50, y1=100, line=dict(color="black", width=1)),
        # Center circle (approximate)
        dict(
            type="circle",
            xref="x", yref="y",
            x0=50-9.15, y0=50-9.15,
            x1=50+9.15, y1=50+9.15,
            line=dict(color="black", width=1)
        ),
        # You can add more shapes for penalty areas, goals, etc.
    ],
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# Display the filtered event data table
st.subheader("Event Data Table")
st.dataframe(df_filtered)
