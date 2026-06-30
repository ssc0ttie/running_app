import streamlit as st
import folium
from streamlit_folium import st_folium
import polyline
from datetime import datetime
import pandas as pd
import numpy as np


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


def create_zone_chart(zones_df, activity_name, activity_date, athlete_name):
    """
    Create HTML visualization for HR and Pace zones.
    zones_df is the DataFrame containing zone data for this specific activity.
    """
    if zones_df is None or zones_df.empty:
        return '<div style="padding: 20px; text-align: center; color: #999;">No zone data available</div>'

    # Debug - uncomment to see actual column names
    st.write(f"Zone columns: {zones_df.columns.tolist()}")

    # DEBUG: Print what we're looking for
    print(
        f"Looking for: Activity='{activity_name}', Date='{activity_date}', Athlete='{athlete_name}'"
    )

    # DEBUG: Print unique values in zones_df
    print(f"Unique Activities in zones_df: {zones_df['Activity'].unique()}")
    print(f"Unique Dates in zones_df: {zones_df['Date_of_Activity'].unique()}")
    print(f"Unique Athletes in zones_df: {zones_df['Member Name'].unique()}")

    # Check for the correct column names (your Zone_Data schema)
    # Possible column names: 'Date_of_Activity', 'Member Name', 'Activity', 'Zone_Type'
    date_col = "Date_of_Activity" if "Date_of_Activity" in zones_df.columns else "Date"
    athlete_col = "Member Name" if "Member Name" in zones_df.columns else "Athlete"
    activity_col = "Activity" if "Activity" in zones_df.columns else "Activity_Name"
    type_col = "Zone_Type" if "Zone_Type" in zones_df.columns else "Type"
    zone_col = "Zone" if "Zone" in zones_df.columns else "Zone"
    zone_name_col = "Zone_Name" if "Zone_Name" in zones_df.columns else "Zone Name"
    min_col = "Min_Value" if "Min_Value" in zones_df.columns else "Min"
    max_col = "Max_Value" if "Max_Value" in zones_df.columns else "Max"
    time_col = "Time_In_Zone" if "Time_In_Zone" in zones_df.columns else "Time"
    pct_col = "Percentage" if "Percentage" in zones_df.columns else "Percentage"

    # Filter zones for this specific activity
    activity_zones = zones_df[
        (zones_df[activity_col].astype(str) == str(activity_name))
        & (zones_df[date_col].astype(str) == str(activity_date))
        & (zones_df[athlete_col].astype(str) == str(athlete_name))
    ]

    if activity_zones.empty:
        return '<div style="padding: 20px; text-align: center; color: #999;">No zone data found</div>'

    # Separate HR and Pace zones
    hr_zones = activity_zones[activity_zones[type_col] == "Heart Rate"]
    pace_zones = activity_zones[activity_zones[type_col] == "Pace"]

    html = '<div style="padding: 15px; background: #fafafa; border-radius: 8px; height: 100%; min-height: 515px;">'

    # HR Zones Section
    if not hr_zones.empty:
        html += """
        <div style="margin-bottom: 20px;">
            <div style="font-weight: 700; font-size: 14px; color: #FC4C02; margin-bottom: 12px;">❤️ HEART RATE ZONES</div>
            <div style="background: white; border-radius: 8px; overflow: hidden;">
                <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
                    <thead>
                        <tr style="background: #f0f0f0;">
                            <th style="padding: 8px; text-align: left;">Zone</th>
                            <th style="padding: 8px; text-align: left;">Range</th>
                            <th style="padding: 8px; text-align: left;">Time</th>
                            <th style="padding: 8px; text-align: left;">%</th>
                         </tr>
                    </thead>
                    <tbody>
        """
        for _, zone in hr_zones.iterrows():
            min_val = zone[min_col] if pd.notna(zone[min_col]) else ""
            max_val = zone[max_col] if pd.notna(zone[max_col]) else ""
            time_val = zone[time_col] if pd.notna(zone[time_col]) else ""
            pct_val = zone[pct_col] if pd.notna(zone[pct_col]) else "0%"
            # Extract numeric percentage for bar width
            pct_num = (
                pct_val.replace("%", "")
                if isinstance(pct_val, str)
                else str(pct_val).replace("%", "")
            )
            try:
                pct_num = float(pct_num)
            except:
                pct_num = 0

            html += f"""
                        <tr style="border-bottom: 1px solid #eee;">
                            <td style="padding: 8px;"><b>{zone[zone_col]}</b><br><span style="font-size: 9px; color: #666;">{zone[zone_name_col]}</span></td>
                            <td style="padding: 8px;">{min_val}-{max_val} bpm</td>
                            <td style="padding: 8px;">{time_val}</td>
                            <td style="padding: 8px;">
                                <div style="display: flex; align-items: center; gap: 6px;">
                                    <div style="width: 50px; background: #e0e0e0; border-radius: 10px; overflow: hidden;">
                                        <div style="width: {pct_num}%; height: 5px; background: #FC4C02;"></div>
                                    </div>
                                    <span>{pct_val}</span>
                                </div>
                             </td>
                         </tr>
            """
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        """

    # Pace Zones Section
    if not pace_zones.empty:
        html += """
        <div>
            <div style="font-weight: 700; font-size: 14px; color: #FC4C02; margin-bottom: 12px;">🏃 PACE ZONES</div>
            <div style="background: white; border-radius: 8px; overflow: hidden;">
                <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
                    <thead>
                        <tr style="background: #f0f0f0;">
                            <th style="padding: 8px; text-align: left;">Zone</th>
                            <th style="padding: 8px; text-align: left;">Pace</th>
                            <th style="padding: 8px; text-align: left;">Time</th>
                            <th style="padding: 8px; text-align: left;">%</th>
                         </tr>
                    </thead>
                    <tbody>
        """
        for _, zone in pace_zones.iterrows():
            min_val = zone[min_col] if pd.notna(zone[min_col]) else ""
            max_val = zone[max_col] if pd.notna(zone[max_col]) else ""
            if max_val and max_val != "-":
                pace_range = f"{min_val} - {max_val}"
            else:
                pace_range = f">{min_val}"
            time_val = zone[time_col] if pd.notna(zone[time_col]) else ""
            pct_val = zone[pct_col] if pd.notna(zone[pct_col]) else "0%"
            pct_num = (
                pct_val.replace("%", "")
                if isinstance(pct_val, str)
                else str(pct_val).replace("%", "")
            )
            try:
                pct_num = float(pct_num)
            except:
                pct_num = 0

            html += f"""
                        <tr style="border-bottom: 1px solid #eee;">
                            <td style="padding: 8px;"><b>{zone[zone_col]}</b><br><span style="font-size: 9px; color: #666;">{zone[zone_name_col]}</span></td>
                            <td style="padding: 8px;">{pace_range}</td>
                            <td style="padding: 8px;">{time_val}</td>
                            <td style="padding: 8px;">
                                <div style="display: flex; align-items: center; gap: 6px;">
                                    <div style="width: 50px; background: #e0e0e0; border-radius: 10px; overflow: hidden;">
                                        <div style="width: {pct_num}%; height: 5px; background: #FC4C02;"></div>
                                    </div>
                                    <span>{pct_val}</span>
                                </div>
                             </td>
                         </tr>
            """
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        """

    html += "</div>"
    return html


def create_activity_card(row, index):
    """
    Create a Strava-style activity card for each activity
    """
    from visuals import generateavatar as avtr

    # Format values
    moving_time_str = format_duration(row["Moving_Time"])
    pace_str = format_pace(row["Pace"])
    max_pace_str = format_max_pace(row["Max_Pace"])
    activity = str(row["Strava_Base_Activity"])
    member = str(row["Member Name"])
    menu = str(row["Menu"])

    menu = row["Menu"] if row["Member Name"] == "Scott" else row["Menu"]

    if row["Member Name"] == "Scott":
        menu = row["Menu"]
    elif row["Member Name"] == "Chona":
        menu = row["Menu"]
    else:
        menu = row["Menu"]
    avatar = avtr.get_member_avatar_advanced(member)

    if hasattr(row["Date_of_Activity"], "strftime"):
        date_str = row["Date_of_Activity"].strftime("%A, %b %d, %Y")
    else:
        date_str = str(row["Date_of_Activity"])

    # Start building the stats HTML - include all stats in one continuous string

    # Start building the stats HTML
    stats_html = f"""
<div style="padding: 20px; background: #fafafa;">
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 20px; margin-bottom: 20px;">
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

    card_html = f"""
    <div style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; overflow: hidden;">
        <div style="padding: 16px 20px; border-bottom: 1px solid #f0f0f0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="width: 40px; height: 40px; background: linear-gradient(135deg, {avatar['color1']}, {avatar['color2']}); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <span style="font-size: 24px;">{avatar['emoji']}</span>
                    </div>
                    <div>
                        <div style="font-weight: 700; font-size: 18px; color: #333;">{member}</div>
                        <div style="font-size: 13px; color: #FC4C02; text-transform: uppercase; letter-spacing: 0.5px;">{activity}</div>
                        <div style="font-size: 14px; color: #555; margin-top: 4px;">🍽️ {menu}</div>
                    </div>
                </div>
                <div style="color: #666; font-size: 13px;">{date_str}</div>
            </div>
        </div>
        {stats_html}
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
                height=200,
                zoom_control=False,  # Remove zoom buttons
                scrollWheelZoom=False,  # Disable mouse wheel zoom
                dragging=False,  # Disable panning/dragging
                touchZoom=False,  # Disable touch zoom on phones
                doubleClickZoom=False,  # Disable double click zoom
                boxZoom=False,  # Disable box zoom
                keyboard=False,  # Disable keyboard controls
            )

            lats = [c[0] for c in coords]
            lngs = [c[1] for c in coords]
            bounds = [[min(lats), min(lngs)], [max(lats), max(lngs)]]

            m.fit_bounds(bounds, padding=(20, 20))  # 20 pixels padding

            m.get_root().html.add_child(folium.Element("""
                <style>
                    .leaflet-tile-pane { opacity: 0.4; }
                    .leaflet-container { background: transparent !important; }
                </style>
            """))

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


def display_strava_style_feed_test(df, zones_df=None):
    """
    Display activities in a Strava-style narrative feed with 3 columns.
    """
    from visuals.generateavatar import get_member_avatar_advanced as avatar

    # Sort by date (most recent first)
    if "Date_of_Activity" in df.columns:
        df = df.sort_values("Date_of_Activity", ascending=False).reset_index(drop=True)

    for index, row in df.iterrows():
        # Create card HTML and map
        card_html, map_obj = create_activity_card(row, index)

        # Use 3 columns
        col_left, col_mid = st.columns([0.5, 0.5])

        with col_left:
            st.markdown(card_html, unsafe_allow_html=True)

            if map_obj:
                st_folium(map_obj, width=None, height=515, key=f"activity_map_{index}")

        with col_mid:
            if zones_df is not None and not zones_df.empty:
                # Get the UniqueKey from the activity row
                parent_key = row.get("UniqueKey", None)

                # Use Parent_UniqueKey for direct matching
                zones_html = create_zone_chart_by_parent_key(zones_df, parent_key)
                # Try st.html if available (Streamlit 1.35+)
                try:
                    st.html(zones_html)
                except AttributeError:
                    st.markdown(zones_html, unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div style="padding: 20px; text-align: center; color: #999; background: #fafafa; border-radius: 8px; height: 515px; display: flex; align-items: center; justify-content: center;">No zone data available<br>Run Strava Sync to calculate zones</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)


def create_zone_chart_by_parent_key(zones_df, parent_unique_key):
    """
    Create HTML visualization for HR and Pace zones using Parent_UniqueKey.
    """
    if zones_df is None or zones_df.empty:
        return '<div style="padding: 20px; text-align: center; color: #999; font-size: 14px;">No zone data available</div>'

    if parent_unique_key is None:
        return '<div style="padding: 20px; text-align: center; color: #999; font-size: 14px;">No parent key available</div>'

    # Find Parent_UniqueKey column
    parent_key_col = None
    for col in zones_df.columns:
        if "Parent" in col and "Key" in col:
            parent_key_col = col
            break

    if parent_key_col is None:
        return '<div style="padding: 20px; text-align: center; color: #999;">Parent_UniqueKey column not found</div>'

    # Filter zones
    activity_zones = zones_df[
        zones_df[parent_key_col].astype(str) == str(parent_unique_key)
    ]

    if activity_zones.empty:
        return f'<div style="padding: 20px; text-align: center; color: #999; font-size: 14px;">No zones found for this activity</div>'

    # Find column names
    type_col = "Zone_Type" if "Zone_Type" in zones_df.columns else "Type"
    zone_col = "Zone" if "Zone" in zones_df.columns else "Zone"
    zone_name_col = "Zone_Name" if "Zone_Name" in zones_df.columns else "Zone Name"
    min_col = "Min_Value" if "Min_Value" in zones_df.columns else "Min"
    max_col = "Max_Value" if "Max_Value" in zones_df.columns else "Max"
    time_col = "Time_In_Zone" if "Time_In_Zone" in zones_df.columns else "Time"
    pct_col = "Percentage" if "Percentage" in zones_df.columns else "Percentage"

    # Separate zones
    hr_zones = activity_zones[activity_zones[type_col] == "Heart Rate"]
    pace_zones = activity_zones[activity_zones[type_col] == "Pace"]

    # Start building HTML
    html = '<div style="padding: 15px; background: #fafafa; border-radius: 8px;">'

    # HR Zones
    if not hr_zones.empty:
        html += '<div style="margin-bottom: 20px;">'
        html += '<div style="font-weight: 700; font-size: 16px; color: #FC4C02; margin-bottom: 12px;">❤️ HEART RATE ZONES</div>'
        html += '<div style="background: white; border-radius: 8px; overflow-x: auto;">'
        html += (
            '<table style="width: 100%; border-collapse: collapse; font-size: 13px;">'
        )
        html += '<thead><tr style="background: #f0f0f0;"><th style="padding: 10px; text-align: left;">Zone</th><th style="padding: 10px; text-align: left;">Range</th><th style="padding: 10px; text-align: left;">Time</th><th style="padding: 10px; text-align: left;">%</th></tr></thead><tbody>'

        for _, zone in hr_zones.iterrows():
            pct_val = str(zone[pct_col]).replace("%", "")
            try:
                pct_num = float(pct_val)
            except:
                pct_num = 0

            html += f'<tr style="border-bottom: 1px solid #eee;">'
            html += f'<td style="padding: 10px;"><b>{zone[zone_col]}</b><br><span style="font-size: 11px; color: #666;">{zone[zone_name_col]}</span></td>'
            html += (
                f'<td style="padding: 10px;">{zone[min_col]}-{zone[max_col]} bpm</td>'
            )
            html += f'<td style="padding: 10px;">{zone[time_col]}</td>'
            html += f'<td style="padding: 10px;"><div style="display: flex; align-items: center; gap: 6px;"><div style="width: 60px; background: #e0e0e0; border-radius: 10px; overflow: hidden;"><div style="width: {pct_num}%; height: 8px; background: #FC4C02;"></div></div><span>{pct_val}%</span></div></td>'
            html += "</tr>"

        html += "</tbody></table></div></div>"

    # Pace Zones
    if not pace_zones.empty:
        html += '<div style="margin-bottom: 10px;">'
        html += '<div style="font-weight: 700; font-size: 16px; color: #FC4C02; margin-bottom: 12px;">🏃 PACE ZONES</div>'
        html += '<div style="background: white; border-radius: 8px; overflow-x: auto;">'
        html += (
            '<table style="width: 100%; border-collapse: collapse; font-size: 13px;">'
        )
        html += '<thead><tr style="background: #f0f0f0;"><th style="padding: 10px; text-align: left;">Zone</th><th style="padding: 10px; text-align: left;">Pace</th><th style="padding: 10px; text-align: left;">Time</th><th style="padding: 10px; text-align: left;">%</th></tr></thead><tbody>'

        for _, zone in pace_zones.iterrows():
            min_val = zone[min_col] if pd.notna(zone[min_col]) else ""
            max_val = zone[max_col] if pd.notna(zone[max_col]) else ""
            if max_val and max_val != "-":
                pace_range = f"{min_val} - {max_val}"
            else:
                pace_range = f">{min_val}"

            pct_val = str(zone[pct_col]).replace("%", "")
            try:
                pct_num = float(pct_val)
            except:
                pct_num = 0

            html += f'<tr style="border-bottom: 1px solid #eee;">'
            html += f'<td style="padding: 10px;"><b>{zone[zone_col]}</b><br><span style="font-size: 11px; color: #666;">{zone[zone_name_col]}</span></td>'
            html += f'<td style="padding: 10px;">{pace_range}</td>'
            html += f'<td style="padding: 10px;">{zone[time_col]}</td>'
            html += f'<td style="padding: 10px;"><div style="display: flex; align-items: center; gap: 6px;"><div style="width: 60px; background: #e0e0e0; border-radius: 10px; overflow: hidden;"><div style="width: {pct_num}%; height: 8px; background: #FC4C02;"></div></div><span>{pct_val}%</span></div></td>'
            html += "</tr>"

        html += "</tbody></table></div></div>"

    html += "</div>"
    return html
