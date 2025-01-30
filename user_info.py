import pandas as pd
import os

# Paths to the CSV files
USER_CSV_FILE = "user_data/all_user_data/all_user_data.csv"

# Ensure the user data CSV file exists
if not os.path.exists(USER_CSV_FILE):
    df = pd.DataFrame(columns=["user_id", "username", "first_name", "last_name"])
    df.to_csv(USER_CSV_FILE, index=False)

# Function to save user data to CSV
def save_user_info(user):
    user_data = {
        "user_id": user.id,
        "username": user.username or "N/A",
        "first_name": user.first_name or "N/A",
        "last_name": user.last_name or "N/A"
    }

    # Read existing data
    df = pd.read_csv(USER_CSV_FILE)

    # Check if user already exists
    if user_data["user_id"] not in df["user_id"].values:
        # Convert the new user data to a DataFrame
        new_data = pd.DataFrame([user_data])

        # Concatenate the new data with the existing DataFrame
        df = pd.concat([df, new_data], ignore_index=True)

        # Save the updated DataFrame to the CSV file
        df.to_csv(USER_CSV_FILE, index=False)
        print(f"Saved user info: {user_data}")