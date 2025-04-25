import streamlit as st
import mysql.connector
import os
import time
from PIL import Image, ImageDraw
import cv2
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Streamlit UI setup
st.set_page_config(page_title="Crowd Dashboard", page_icon=":bar_chart:", layout="wide")

st.markdown("""
    <style>
        /* Main content background */
        .main {
            background-color: #192134;
        }

        /* Sidebar background */
        section[data-testid="stSidebar"] {
            background-color: #111927;
        }

        /* Sidebar title and other text color */
        .css-1cpxqw2, .css-1d391kg, .css-hxt7ib {
            color: white;
        }

        /* Make all text white inside main content */
        h1, h2, h3, h4, h5, h6, p, div, span {
            color: white;
        }

        /* Fix for download button and other Streamlit elements */
        .stButton>button, .stDownloadButton>button {
            color: white;
            background-color: #2A2D3E;
        }
    </style>
""", unsafe_allow_html=True)


# Define video paths and gate colors
Video_paths = {
    "Gate_A": r"C:\\Users\\fa15s\\OneDrive\\Documents\\Visual-Projects\\PythonProjects\\SAF_Project_Mofawij\\Test6.png",
    "Gate_B": r"C:\\Users\\fa15s\\OneDrive\\Documents\\Visual-Projects\\PythonProjects\\SAF_Project_Mofawij\\Test5.png",
    "Gate_C": r"C:\\Users\\fa15s\\OneDrive\\Documents\\Visual-Projects\\PythonProjects\\SAF_Project_Mofawij\\Test8.png",
    "Gate_D": r"C:\\Users\\fa15s\\OneDrive\\Documents\\Visual-Projects\\PythonProjects\\SAF_Project_Mofawij\\TestD.png",
}

Gate_Colors = {
    "LOW": "green",
    "MEDIUM": "yellow",
    "HIGH": "red",
    "UNKNOWN": "white",
}

# Fetch data from MySQL
def get_random_data(gate_name):
    conn = mysql.connector.connect(
        host="localhost",
        user="mofawij_user",
        password="0980",
        database="mofawij_db",
    )
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT * FROM crowd_log
    WHERE gate_zone = %s
    ORDER BY RAND() LIMIT 1
    """
    cursor.execute(query, (gate_name,))
    row = cursor.fetchone()
    conn.close()
    return row

# Load image for a specific video path
def load_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None

# Draw map overlay
def draw_map_overlay(img_path, gate_status):
    image = Image.open(img_path).convert("RGBA")
    image = image.resize((1200, 800))
    draw = ImageDraw.Draw(image)

    gate_coords = {
        "Gate_A": (450, 240),
        "Gate_B": (850, 300),
        "Gate_C": (350, 500),
        "Gate_D": (750, 550)
    }

    for gate, coord in gate_coords.items():
        status = gate_status.get(gate, {"level": "UNKNOWN"})
        color = Gate_Colors.get(status["level"], "white")
        draw.ellipse([coord[0]-8, coord[1]-8, coord[0]+8, coord[1]+8], fill=color)
        draw.text((coord[0]+10, coord[1]-10), f"{gate}\n{status['label']}", fill="white")

    return image

# ======= Sidebar Navigation (Box style) =======
st.sidebar.title("Mofawij - King Fahad Stadium ")
st.sidebar.image(
    "C:\\Users\\fa15s\\OneDrive\\Documents\\Visual-Projects\\PythonProjects\\SAF_Project_Mofawij\\Mofawij.png",
    use_container_width=True
)
dashboard_btn = st.sidebar.button("\U0001F4CA Crowd Dashboard", use_container_width=True)
map_btn = st.sidebar.button("\U0001F5FA️ Stadium Map", use_container_width=True)

show_dashboard = dashboard_btn or (not dashboard_btn and not map_btn)
show_map = map_btn

# ======= Crowd Dashboard View =======
if show_dashboard:
    st.subheader("\U0001F9CD Real-Time Gate Monitoring")
    gate_names = ["Gate_A", "Gate_B", "Gate_C", "Gate_D"]

    columns = st.columns(4)
    for i, gate in enumerate(gate_names):
        with columns[i]:
            st.markdown(f"#### {gate}")

            data = get_random_data(gate)
            if data:
                st.markdown(f"**People Passed the Gate:** {data['people_below_line']}")
                st.markdown(f"**Congestion Level:** {data['congestion_level']}")
                st.markdown(f"**Density:** {data['density']:.2f} people/m²")
                st.markdown(f"**Gate Status:** {data['gate_status']}")
                fill = min(data['people_below_line'] / 250, 1.0)
                st.progress(fill, text=f"{data['congestion_level']} - {int(fill*100)}%")
            else:
                st.markdown(f"**People Passed the Gate:** N/A")
                st.markdown(f"**Congestion Level:** N/A")
                st.markdown(f"**Density:** N/A people/m²")
                st.markdown(f"**Gate Status:** \U0001F6A7 **Under Maintenance**")
                st.progress(0, text=f"N/A - 0%")

            frame = None
            if gate in Video_paths and os.path.exists(Video_paths[gate]):
                frame = load_frame(Video_paths[gate])

            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width = frame.shape[:2]
                frame = cv2.resize(frame, (400, int(400 * height / width)))
                st.image(frame, caption=f"{gate} Live Feed")
            else:
                if gate == "Gate_D":
                    st.markdown("\U0001F6A7 Gate D feed not available - Maintenance")
                else:
                    st.markdown("\U0001F50C Image not available")

    st.markdown("---")
    st.subheader(":bar_chart: Gate-Level Summary")

    conn = mysql.connector.connect(
        host="localhost",
        user="mofawij_user",
        password="0980",
        database="mofawij_db",
    )
    df = pd.read_sql("SELECT * FROM crowd_log", conn)
    conn.close()

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### Total Crossings Per Gate")
        fig, ax = plt.subplots(facecolor='#162133')
        df.groupby('gate_zone')['people_below_line'].sum().sort_values().plot(kind='barh', ax=ax, color='salmon', edgecolor='white')
        ax.set_facecolor('#162133')
        fig.patch.set_alpha(0)
        ax.set_title("People Who Crossed Line", color='white')
        ax.set_xlabel("Total", color='white')
        ax.set_ylabel("gate_zone", color='white')
        ax.tick_params(colors='white')
        st.pyplot(fig)

    with chart_col1:
        st.markdown("#### Average People Count Per Gate")
        fig, ax = plt.subplots(facecolor='#162133')
        df.groupby('gate_zone')['people_count'].mean().plot(kind='bar', ax=ax, color='skyblue', edgecolor='white')
        ax.set_facecolor('#162133')
        fig.patch.set_alpha(0)
        ax.set_title("Average Crowd Size", color='white')
        ax.set_ylabel("People", color='white')
        ax.set_xlabel("Gate", color='white')
        ax.tick_params(colors='white')
        st.pyplot(fig)

    with chart_col2:
        st.markdown("#### People Count Distribution Per Gate")
        fig, ax = plt.subplots(facecolor='#162133')
        df.boxplot(column='people_count', by='gate_zone', ax=ax, patch_artist=True)
        ax.set_facecolor('#162133')
        fig.patch.set_alpha(0)
        ax.set_title("Crowd Count Variability", color='white')
        ax.set_ylabel("People Count", color='white')
        ax.set_xlabel("Gate", color='white')
        ax.tick_params(colors='white')
        plt.suptitle("")
        st.pyplot(fig)

    with chart_col2:
        st.markdown("#### Total Alerts Per Gate")
        fig, ax = plt.subplots(facecolor='#162133')
        df.groupby(['gate_zone', 'alert_triggered']).size().unstack(fill_value=0).plot(kind='bar', stacked=True, ax=ax)
        ax.set_facecolor('#162133')
        fig.patch.set_alpha(0)
        ax.set_title("Alert Distribution", color='white')
        ax.set_ylabel("Alerts", color='white')
        ax.set_xlabel("Gate", color='white')
        ax.tick_params(colors='white')
        st.pyplot(fig)
