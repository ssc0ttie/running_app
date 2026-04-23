import streamlit_folium as st_folium
import streamlit as st
import folium
import polyline


def generate_polyline(df):
    # Check if the column exists and isn't empty
    if "Map_Polyline" not in df.columns:
        return None

    for index, row in df.iterrows():
        poly_str = row["Map_Polyline"]

        # Check if poly_str is valid (not None or NaN)
        if poly_str and isinstance(poly_str, str):
            try:
                coords = polyline.decode(poly_str)

                # COMBINE tiles, location, and any other map settings here
                m = folium.Map(
                    location=coords[0],
                    tiles=None,
                    attr="Clean Plot",
                    control_scale=True,
                    zoom_start=14,
                )

                folium.PolyLine(
                    coords,
                    color="#FC4C02",
                    weight=4,
                    opacity=0.8,
                ).add_to(m)

                # Display in Streamlit
                st_folium.st_folium(m, width=1000, height=350, key=f"map_{index}")

            except Exception as e:
                st.error(f"Error decoding polyline at index {index}: {e}")


def generate_polyline_transparent(df, tile_opacity=0.5):
    if "Map_Polyline" not in df.columns:
        return None

    for index, row in df.iterrows():
        poly_str = row["Map_Polyline"]

        if poly_str and isinstance(poly_str, str):
            try:
                coords = polyline.decode(poly_str)

                m = folium.Map(
                    location=coords[0],
                    tiles="CartoDB positron",  # Light tiles that work well with transparency
                    control_scale=True,
                    zoom_start=14,
                )

                # Create dynamic opacity control
                opacity_style = f"""
                <style>
                    .leaflet-tile-pane {{
                        opacity: {tile_opacity};
                    }}
                    .leaflet-container {{
                        background: transparent !important;
                    }}
                    /* Optional: make attribution smaller and semi-transparent */
                    .leaflet-control-attribution {{
                        opacity: 0.5;
                        font-size: 8px;
                    }}
                </style>
                """

                m.get_root().html.add_child(folium.Element(opacity_style))

                folium.PolyLine(
                    coords,
                    color="#FC4C02",
                    weight=4,
                    opacity=0.8,
                ).add_to(m)

                st_folium.st_folium(m, width=1000, height=350, key=f"map_{index}")

            except Exception as e:
                st.error(f"Error decoding polyline at index {index}: {e}")
