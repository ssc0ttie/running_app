import streamlit as st
import folium
from streamlit_folium import st_folium
import polyline
from datetime import datetime
import pandas as pd


def format_duration(duration):
    """
    Convert timedelta to a readable string format (HH:MM:SS or MM:SS)
    """
    if pd.isna(duration):
        return "N/A"

    if isinstance(duration, str):
        return duration

    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


def format_pace(pace):
    """
    Format pace from timedelta or string to MM:SS format
    """
    if pd.isna(pace):
        return "N/A"

    if isinstance(pace, str):
        if ":" in pace and "day" not in pace.lower():
            return pace
        return pace

    total_seconds = int(pace.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    return f"{minutes:02d}:{seconds:02d}"


def format_max_pace(max_pace):
    """
    Specifically format max pace to ensure no hours
    """
    if pd.isna(max_pace):
        return "N/A"

    # If it's already a formatted string
    if isinstance(max_pace, str):
        parts = max_pace.split(":")
        if len(parts) == 3:  # HH:MM:SS
            # Convert hours to minutes
            total_minutes = int(parts[0]) * 60 + int(parts[1])
            return f"{total_minutes:02d}:{int(parts[2]):02d}"
        elif len(parts) == 2:  # MM:SS
            return max_pace
        return max_pace

    # If it's a timedelta
    if hasattr(max_pace, "total_seconds"):
        total_seconds = int(max_pace.total_seconds())
        total_seconds = total_seconds % 3600  # Remove hours
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    # If it's a number
    if isinstance(max_pace, (int, float)):
        total_seconds = int(max_pace)
        total_seconds = total_seconds % 3600
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    return str(max_pace)


def create_activity_card(row, index):
    """
    Create a Strava-style activity card for each activity
    """

    # Format values
    moving_time_str = format_duration(row["Moving_Time"])
    pace_str = format_pace(row["Pace"])
    max_pace_str = format_max_pace(row["Max_Pace"])
    activity = str(row["Activity"])

    if hasattr(row["Date_of_Activity"], "strftime"):
        date_str = row["Date_of_Activity"].strftime("%A, %b %d, %Y")
    else:
        date_str = str(row["Date_of_Activity"])

    # Start building the stats HTML - include all stats in one continuous string

    stats_html_3 = f"""
<div style="padding: 20px; background: #fafafa;">
    <!-- Responsive Metrics Grid -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin-bottom: 20px;">
        <div>
            <div style="font-size: 24px; font-weight: 700; color: #FC4C02;">{row['Distance']:.1f}</div>
            <div style="font-size: 12px; color: #666; text-transform: uppercase;">Distance (km)</div>
        </div>
        <div>
            <div style="font-size: 24px; font-weight: 700; color: #FC4C02;">{moving_time_str}</div>
            <div style="font-size: 12px; color: #666; text-transform: uppercase;">Moving Time</div>
        </div>
        <div>
            <div style="font-size: 24px; font-weight: 700; color: #FC4C02;">{pace_str}</div>
            <div style="font-size: 12px; color: #666; text-transform: uppercase;">Avg Pace</div>
        </div>
        <div>
            <div style="font-size: 24px; font-weight: 700; color: #FC4C02;">{row['HR (bpm)']:.0f}</div>
            <div style="font-size: 12px; color: #666; text-transform: uppercase;">Avg HR</div>
        </div>
        <div>
            <div style="font-size: 24px; font-weight: 700; color: #FC4C02;">{row['Cadence (steps/min)']:.0f}</div>
            <div style="font-size: 12px; color: #666; text-transform: uppercase;">Cadence</div>
        </div>
        <div>
            <div style="font-size: 24px; font-weight: 700; color: #FC4C02;">{max_pace_str}</div>
            <div style="font-size: 12px; color: #666; text-transform: uppercase;">Max Pace</div>
        </div>
        <div>
            <div style="font-size: 24px; font-weight: 700; color: #FC4C02;">{row['Max_HR']:.0f}</div>
            <div style="font-size: 12px; color: #666; text-transform: uppercase;">Max HR</div>
        </div>
        <div>
            <div style="font-size: 24px; font-weight: 700; color: #FC4C02;">{row['Elevation_Gained']:.0f}</div>
            <div style="font-size: 12px; color: #666; text-transform: uppercase;">Elevation Gained</div>
        </div>
    </div>
    </div>
    <div style="padding: 12px 20px; background: #f9f9f9; border-top: 1px solid #f0f0f0; color: #555; font-size: 16px; font-style: italic;">
        💭 {row['Remarks']}
    </div>
</div>
"""
    # Complete card HTML - put everything together
    card_html = f"""
    <div style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; overflow: hidden;">
        <div style="padding: 16px 20px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 24px;">🏃</span>
                <span style="font-weight: 600; font-size: 22px; color: #333;">{activity}</span>
            </div>
            <div style="color: #666; font-size: 14px;">{date_str}</div>
        </div>
        {stats_html_3}
  
   
    """

    # Decode polyline for map
    map_object = None
    if "Map_Polyline" in row and row["Map_Polyline"]:
        try:
            coords = polyline.decode(row["Map_Polyline"])

            m = folium.Map(
                location=coords[0],
                tiles="CartoDB positron",
                control_scale=True,
                # zoom_start=13,
                width="100%",
                height=250,
                zoom_control=True,  # Keep buttons visible
                scrollWheelZoom=False,  # Disable scroll wheel
                touchZoom=False,  # Disable pinch zoom
                doubleClickZoom=False,  # Disable double click
                dragging=True,  # Allow panning (less intrusive)
            )

            lats = [c[0] for c in coords]
            lngs = [c[1] for c in coords]
            bounds = [[min(lats), min(lngs)], [max(lats), max(lngs)]]

            m.fit_bounds(bounds, padding=(20, 20))  # 20 pixels padding

            m.get_root().html.add_child(
                folium.Element(
                    """
                <style>
                    .leaflet-tile-pane { opacity: 0.4; }
                    .leaflet-container { background: transparent !important; }
                </style>
            """
                )
            )

            folium.PolyLine(
                coords,
                color="#c17b4f",
                weight=5,
                opacity=0.9,
                popup=f"{row['Distance']:.1f} km",
            ).add_to(m)

            folium.Marker(
                coords[0],
                icon=folium.Icon(color="green", icon="play", prefix="fa"),
                popup="Start",
            ).add_to(m)

            folium.Marker(
                coords[-1],
                icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa"),
                popup="Finish",
            ).add_to(m)

            map_object = m

        except Exception as e:
            st.error(f"Error loading map for activity on {date_str}: {e}")

    return card_html, map_object


def display_strava_style_feed(df):
    """
    Display activities in a Strava-style narrative feed
    """

    # Sort by date (most recent first)
    if "Date_of_Activity" in df.columns:
        df = df.sort_values("Date_of_Activity", ascending=False).reset_index(drop=True)

    # st.markdown("### 🏃 Recent Activities")

    for index, row in df.iterrows():
        # Create card HTML and map
        card_html, map_obj = create_activity_card(row, index)

        # Display the card using the same method as the test card
        st.markdown(card_html, unsafe_allow_html=True)

        # Display map if it exists
        if map_obj:
            st_folium(map_obj, width=None, height=250, key=f"activity_map_{index}")

        # Add spacing
        st.markdown("<br>", unsafe_allow_html=True)


def display_strava_style_feed_test(df):
    """
    Display activities in a Strava-style narrative feed
    """

    # Sort by date (most recent first)
    if "Date_of_Activity" in df.columns:
        df = df.sort_values("Date_of_Activity", ascending=False).reset_index(drop=True)

    # st.markdown("### 🏃 Recent Activities")

    for index, row in df.iterrows():
        # Create card HTML and map
        card_html, map_obj = create_activity_card(row, index)

        col_left, col_right = st.columns([0.4, 0.6])
        # Display the card using the same method as the test card
        with col_left:
            st.markdown(card_html, unsafe_allow_html=True)

        # Display map if it exists
        with col_right:
            if map_obj:
                st_folium(map_obj, width=None, height=515, key=f"activity_map_{index}")

        # Add spacing
        st.markdown("<br>", unsafe_allow_html=True)


def display_strava_style_feed_new(df):
    """
    Display activities in a Strava-style narrative feed with map on the right
    """

    # Sort by date (most recent first)
    if "Date_of_Activity" in df.columns:
        df = df.sort_values("Date_of_Activity", ascending=False).reset_index(drop=True)

    st.markdown("### 🏃 Recent Activities")

    for index, row in df.iterrows():
        # Create two columns - left for stats (40%), right for map (60%)
        col_left, col_right = st.columns([0.4, 0.6])

        # Format values
        moving_time_str = format_duration(row["Moving_Time"])
        pace_str = format_pace(row["Pace"])

        if hasattr(row["Date_of_Activity"], "strftime"):
            date_str = row["Date_of_Activity"].strftime("%A, %b %d, %Y")
        else:
            date_str = str(row["Date_of_Activity"])

        # Build HR and Cadence HTML
        hr_html = (
            f"""
        <div style="margin-bottom: 12px;">
            <div style="font-size: 20px; font-weight: 700; color: #FC4C02;">{row['HR (bpm)']:.0f}</div>
            <div style="font-size: 11px; color: #666; text-transform: uppercase;">Avg HR</div>
        </div>
        """
            if pd.notna(row.get("HR (bpm)"))
            else ""
        )

        cadence_html = (
            f"""
        <div>
            <div style="font-size: 20px; font-weight: 700; color: #FC4C02;">{row['Cadence (steps/min)']:.0f}</div>
            <div style="font-size: 11px; color: #666; text-transform: uppercase;">Cadence</div>
        </div>
        """
            if pd.notna(row.get("Cadence (steps/min)"))
            else ""
        )

        # LEFT COLUMN - Stats Card
        with col_left:
            card_html = f"""
            <div style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; height: 100%;">
                <div style="padding: 12px 16px; border-bottom: 1px solid #f0f0f0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 20px;">🏃</span>
                            <span style="font-weight: 600; font-size: 14px; color: #333;">Run</span>
                        </div>
                        <div style="color: #666; font-size: 12px;">{date_str}</div>
                    </div>
                </div>
                
                <div style="padding: 16px;">
                    <div style="margin-bottom: 16px;">
                        <div style="font-size: 28px; font-weight: 700; color: #FC4C02;">{row['Distance']:.1f}</div>
                        <div style="font-size: 11px; color: #666; text-transform: uppercase;">Distance (km)</div>
                    </div>
                    
                    <div style="margin-bottom: 16px;">
                        <div style="font-size: 20px; font-weight: 700; color: #FC4C02;">{moving_time_str}</div>
                        <div style="font-size: 11px; color: #666; text-transform: uppercase;">Moving Time</div>
                    </div>
                    
                    <div style="margin-bottom: 16px;">
                        <div style="font-size: 20px; font-weight: 700; color: #FC4C02;">{pace_str}</div>
                        <div style="font-size: 11px; color: #666; text-transform: uppercase;">Avg Pace</div>
                    </div>
                    
                    <div style="display: flex; gap: 20px; margin-top: 16px; padding-top: 12px; border-top: 1px solid #f0f0f0;">
                        {hr_html}
                        {cadence_html}
                    </div>
                </div>
                
                {f'''
                <div style="padding: 10px 16px; background: #f9f9f9; border-top: 1px solid #f0f0f0; color: #555; font-size: 12px; font-style: italic;">
                    💭 {row['Remarks']}
                </div>
                ''' if pd.notna(row.get('Remarks')) and row.get('Remarks') else ''}
            </div>
            """

            st.markdown(card_html, unsafe_allow_html=True)

        # RIGHT COLUMN - Map
        with col_right:
            if "Map_Polyline" in row and row["Map_Polyline"]:
                try:
                    coords = polyline.decode(row["Map_Polyline"])

                    m = folium.Map(
                        location=coords[0],
                        tiles="CartoDB positron",
                        control_scale=True,
                        zoom_start=13,
                        width="100%",
                        height="100%",
                    )

                    # Add transparency styling
                    m.get_root().html.add_child(
                        folium.Element(
                            """
                        <style>
                            .leaflet-tile-pane { opacity: 0.4; }
                            .leaflet-container { background: transparent !important; }
                        </style>
                    """
                        )
                    )

                    # Add the route
                    folium.PolyLine(
                        coords,
                        color="#FC4C02",
                        weight=5,
                        opacity=0.9,
                        popup=f"{row['Distance']:.1f} km",
                    ).add_to(m)

                    # Add start marker
                    folium.Marker(
                        coords[0],
                        icon=folium.Icon(color="green", icon="play", prefix="fa"),
                        popup="Start",
                    ).add_to(m)

                    # Add end marker
                    folium.Marker(
                        coords[-1],
                        icon=folium.Icon(
                            color="red", icon="flag-checkered", prefix="fa"
                        ),
                        popup="Finish",
                    ).add_to(m)

                    st_folium(m, width=None, height=350, key=f"activity_map_{index}")

                except Exception as e:
                    st.warning(f"Map not available: {e}")
            else:
                st.info("No map data available for this activity")

        # Add spacing between activities
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
