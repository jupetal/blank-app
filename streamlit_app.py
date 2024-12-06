import streamlit as st
import requests
import pandas as pd
from PIL import Image
import os

# API Configuration
API_URL = "https://api.api-ninjas.com/v1/cars"
API_KEY = "dTBeNhXpC6bFLLAETGRvqA==7EI4SiZ6EQCECUFv"

# Paths
IMAGE_DIRECTORY = r"C:\Users\Leona\CarDataset\the-car-connection-picture-dataset"
CSV_PATH = os.path.join(IMAGE_DIRECTORY, "cars_metadata.csv")

# Predefined car classes
CAR_CLASSES = [
    "Compact Car",
    "Midsize Car",
    "Minicompact Car",
    "Minivan",
    "Small Sport Utility Vehicle",
    "Standard Sport Utility Vehicle",
    "Subcompact Car",
    "Two Seater"
]

# Fetch car data from the API for a single year
def fetch_car_data(year, filters):
    headers = {'X-Api-Key': API_KEY}
    filters['year'] = year
    response = requests.get(API_URL, headers=headers, params=filters)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data from the API. Status code: {response.status_code}")
        st.write("Response content:", response.text)
        return []

# Load image metadata
@st.cache_data
def load_image_metadata():
    """
    Load car image metadata from a CSV file.
    """
    try:
        return pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        st.error("Image metadata file not found. Ensure the CSV file is available.")
        return pd.DataFrame()

# Match car name/model with an image
def get_car_image(metadata, make, model):
    """
    Match car image based on make and model using metadata.
    """
    query = f"{make} {model}".lower()
    for _, row in metadata.iterrows():
        if query in row['car_name'].lower():
            return os.path.join(IMAGE_DIRECTORY, row['image_path'])
    return None
st.set_page_config(layout = "wide")
# Streamlit app
st.markdown(
    """
    <style>
    .full-width-title {
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        color: #4CAF50;
        padding: 10px;
        background-color: #f4f4f4;
        margin-bottom: 20px;
        border-radius: 5px;
        width: 100%;
    }
    </style>
    <div class="full-width-title">AutoMatch: Your Personalized Car Finder</div>
    """,
    unsafe_allow_html=True,
)

# Input Section: Preferences
st.header("Find Your Perfect Match")

# Year range slider
st.subheader("Model Year")
year_range = st.slider("Select Year Range:", min_value=1980, max_value=2024, value=(2000, 2024), step=1)

# Car class selection
st.subheader("Car Class")
selected_class = st.selectbox("Select a car class:", [""] + CAR_CLASSES)

# Car maker input
st.subheader("Car Maker (Optional)")
selected_maker = st.text_input("Enter the maker of the car (e.g., Toyota, Ford) (Optional):")

# Alphabetically ordered preferences
st.subheader("Engine Size")
cylinders = st.selectbox("Number of Cylinders (Optional):", ["", 2, 3, 4, 5, 6, 8, 10, 12, 16])
st.subheader("Drivetrain")
drive = st.selectbox("Drive Type (Optional):", ["", "FWD", "RWD", "AWD"])

# Fuel type options (Electric, Gas, Diesel)
st.subheader("Fuel Type")
electric = st.checkbox("Electric")
gas = st.checkbox("Gas")
diesel = st.checkbox("Diesel")

# MPG filters
st.subheader("Fuel Economy")
min_comb_mpg = st.number_input("Minimum Combined MPG (Optional):", min_value=0, max_value=100, step=1, value=0)
max_comb_mpg = st.number_input("Maximum Combined MPG (Optional):", min_value=0, max_value=100, step=1, value=100)

# Transmission type
st.subheader("Gearbox/Transmission Type")
transmission = st.selectbox("Transmission Type (Optional):", ["", "Manual", "Automatic"])

# Fetch cars based on preferences
if st.button("Find Match"):
    st.info("Fetching car data from the API...")
    
    # Build filters
    filters = {}
    if min_comb_mpg > 0:
        filters['min_comb_mpg'] = min_comb_mpg
    if max_comb_mpg < 100:
        filters['max_comb_mpg'] = max_comb_mpg
    filters['min_year'], filters['max_year'] = year_range
    if electric:
        filters['fuel_type'] = 'electric'
    if gas:
        filters['fuel_type'] = 'gas'
    if diesel:
        filters['fuel_type'] = 'diesel'
    if transmission:
        filters['transmission'] = 'm' if transmission == "manual" else 'a'
    if drive:
        filters['drive'] = drive
    if cylinders:
        filters['cylinders'] = cylinders
    if selected_class:
        filters['class'] = selected_class
    if selected_maker:
        filters['make'] = selected_maker

    # Fetch cars for each year in the range
    all_cars = []
    for year in range(year_range[0], year_range[1] + 1):
        cars = fetch_car_data(year, filters)
        if cars:
            all_cars.extend(cars)
    
    # Combine results into a DataFrame for local filtering
    if all_cars:
        cars_df = pd.DataFrame(all_cars)

        # Limit results to 10 cars
        cars_df = cars_df.head(10)

        if not cars_df.empty:
            st.success(f"Found {len(cars_df)} cars matching your preferences (showing top 10):")
            
            # Load image metadata
            metadata = load_image_metadata()

            # Display results
            for _, car in cars_df.iterrows():
                cols = st.columns([1, 2])  # Two columns: image on the left, details on the right
                with cols[0]:
                    # Fetch and display car image
                    image_path = get_car_image(metadata, car["make"], car["model"])
                    if image_path and os.path.exists(image_path):
                        image = Image.open(image_path)
                        st.image(image, use_column_width=True)
                    else:
                        st.warning("Image not available for this car.")
                with cols[1]:
                    # Display car details
                    st.subheader(f"{car['make']} {car['model']}")
                    st.write(f"**Year**: {car['year']}")
                    st.write(f"**Fuel Type**: {car.get('fuel_type', 'N/A')}")
                    st.write(f"**Class**: {car.get('class', 'N/A')}")
                    st.write(f"**Transmission**: {car['transmission']}")
                    st.write(f"**Drive**: {car.get('drive', 'N/A')}")
                    st.write(f"**Cylinders**: {car.get('cylinders', 'N/A')}")
                    st.write(f"**Combined MPG**: {car.get('combination_mpg', 'N/A')}")
                    st.markdown("---")
        else:
            st.warning("No cars match your criteria.")
    else:
        st.warning("No cars found in the selected year range.")
