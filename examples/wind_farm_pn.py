from datetime import datetime, timedelta
import pandas as pd
from elexonpy.api_client import ApiClient
from elexonpy.api.balancing_mechanism_physical_api import BalancingMechanismPhysicalApi

# Initialize API client
api_client = ApiClient()

# Initialize the Balancing Mechanism Physical API
physical_api = BalancingMechanismPhysicalApi(api_client)

# Define dataset and settlement period parameters
dataset = 'PN'  # Physical Notification dataset
settlement_date = datetime.now().strftime('%Y-%m-%d')
settlement_period = 1  # Example settlement period (1-50)

# Fetch market-wide physical data for all BM Units
print(f"Fetching physical data for settlement date {settlement_date} and period {settlement_period}...")
physical_data = physical_api.balancing_physical_all_get(
    dataset=dataset,
    settlement_date=settlement_date,
    settlement_period=settlement_period,
    format='dataframe'
)

# Debug: Print columns in the DataFrame
print("Columns in the returned DataFrame:", physical_data.columns)

# Filter for wind farms based on available columns
if 'bm_unit' in physical_data.columns:
    # Assuming 'bm_unit' contains identifiers for BM Units, filter for wind farms
    wind_farms = physical_data[physical_data['bm_unit'].str.contains('WIND', case=False, na=False)]
else:
    print("No 'bm_unit' column found. Please check API response structure.")
    wind_farms = pd.DataFrame()  # Empty DataFrame as fallback

# Print available wind farms
print(f"Found {len(wind_farms)} wind farms")
print(wind_farms.head())

# Select one wind farm (first one in the list for this example)
if not wind_farms.empty:
    selected_wind_farm = wind_farms.iloc[0]['bm_unit']
    print(f"\nSelected wind farm: {selected_wind_farm}")

    # Define time range for data retrieval (last 24 hours)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)

    # Fetch PN data specifically for the selected wind farm over the time range
    print(f"\nFetching PN data for {selected_wind_farm} from {start_time} to {end_time}")
    try:
        wind_data = physical_api.balancing_physical_get(
            bm_unit=[selected_wind_farm],
            _from=start_time.isoformat(),
            to=end_time.isoformat(),
            dataset=['PN'],  # Specifically requesting Physical Notification data
            format='dataframe'
        )

        # Display the results
        if not wind_data.empty:
            print(f"\nPN data for wind farm {selected_wind_farm}:")
            print(wind_data.head())

            # Calculate some basic statistics
            print("\nSummary statistics:")
            print(f"Mean output: {wind_data['level'].mean():.2f} MW")
            print(f"Max output: {wind_data['level'].max():.2f} MW")
            print(f"Min output: {wind_data['level'].min():.2f} MW")
        else:
            print(f"No PN data found for wind farm {selected_wind_farm} in the specified time period.")
    except Exception as e:
        print(f"Error fetching PN data: {e}")
else:
    print("No wind farms found in the provided dataset.")
