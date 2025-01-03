import pandas as pd
from datetime import datetime
import os
import json


class PreprocessingOfData:
    def __init__(self, ClientData:dict) -> None: 
        """
        Initializes the PreprocessingOfData class by loading data and setting up necessary fields.

        Parameters:
        csv_file_path (str): The file path of the CSV file containing client data. Defaults to "../data/Data_from_Client.csv".
        """

        self.Client_data = pd.DataFrame(ClientData, columns=ClientData.keys())

        # Initialize Data_of_Rule_test to None
        self.Data_of_Rule_test = None
        # Create ABN and GST dates, calculate Asset age
        if self.Client_data is not None:
            self.create_abn_gst_dates()
            self.create_asset_categories()
            self.create_asset_classification()
            self.create_Deposit_Amount_Percentage()

    def Asset_category_classification(self, Asset, Lender_name, Asset_category):
        if Asset.upper() in [category.upper().strip() for category in self.asset_categories[Lender_name][Asset_category].split(",")]:
            return True
        return False

    def create_asset_categories(self):
        with open('static/data.json', 'r') as file:
            self.asset_categories = json.load(file)

        def CategoryAsset(asset):
            asset_upper = asset.upper()
            if asset_upper in self.asset_categories["Primary"]:
                return "PRIMARY_ASSETS"
            elif asset_upper in self.asset_categories["Secondary"]:
                return "SECONDARY_ASSETS"
            elif asset_upper in self.asset_categories["Tertiary"]:
                return "TERTIARY_ASSETS"
            else:
                return "Unknown"
        self.Client_data["asset_category"] = self.Client_data["asset_type"].apply(CategoryAsset)

    def create_asset_classification(self):
        with open('Preprocessing_Data.json', 'r') as file:
            self.asset_classes = json.load(file)

        def classify_asset(asset):
            asset_upper = asset.upper()
            if asset_upper in self.asset_classes["Motor_Vehicles"]:
                return "Motor_Vehicles"
            elif asset_upper in self.asset_classes["Primary_Assets"]:
                return "Primary_Assets"
            else:
                return "Unknown"

        self.Client_data['Asset_classification'] = self.Client_data['asset_type'].apply(classify_asset)

    def create_Deposit_Amount_Percentage(self):
        self.Client_data['deposit_amount'] = pd.to_numeric(self.Client_data['deposit_amount'], errors='coerce')
        self.Client_data['amount_financed'] = pd.to_numeric(self.Client_data['amount_financed'], errors='coerce')
        self.Client_data["Deposit_Amount_percentage"] = (self.Client_data['deposit_amount'].fillna(0) / self.Client_data['amount_financed'])

    def create_abn_gst_dates(self, current_year=datetime.now().year, current_date=pd.to_datetime(datetime.now().strftime('%d-%m-%Y'), dayfirst=True)):
        """
        Calculates asset age and the number of months for GST and ABN registration.

        Parameters:
        current_year (int): The current year to calculate the asset age. Defaults to the current year.
        current_date (pd.Timestamp): The current date to calculate the number of months for GST and ABN registration. Defaults to today's date.
        """
        if current_year is None:
            current_year = datetime.now().year
        if current_date is None:
            current_date = pd.to_datetime(datetime.now().strftime('%d-%m-%Y'))

        try:
            # Ensure the 'asset_manufacture_year' column is numeric
            self.Client_data['asset_manufacture_year'] = pd.to_numeric(self.Client_data['asset_manufacture_year'], errors='coerce')
            self.Client_data['repayment_term_month'] = pd.to_numeric(self.Client_data['repayment_term_month'], errors='coerce')
            # Check for any NaN values after conversion
            if self.Client_data['asset_manufacture_year'].isnull().any():
                raise ValueError("Invalid or missing values in 'asset_manufacture_year' column.")
            # Calculate the asset age based on the current year and asset manufacture year
            self.Client_data['Asset_age'] = current_year - self.Client_data['asset_manufacture_year']
            self.Client_data["Asset_age_at_end_of_term"] = self.Client_data["Asset_age"] + self.Client_data['repayment_term_month'] / 12
            # Convert GST and ABN registration dates from string to datetime format
            self.Client_data['gst_registered_date'] = pd.to_datetime(self.Client_data['gst_registered_date'], format='%Y-%m-%d', errors='coerce')
            self.Client_data['abn_registered_date'] = pd.to_datetime(self.Client_data['abn_registered_date'], format='%Y-%m-%d', errors='coerce')

            # Check for invalid dates
            if self.Client_data[['gst_registered_date', 'abn_registered_date']].isnull().any().any():
                raise ValueError("Invalid or missing dates in 'gst_registered_date' or 'abn_registered_date' columns.")

            # Calculate the number of months since GST registration
            self.Client_data['GST_in_Months'] = (current_date.year - self.Client_data['gst_registered_date'].dt.year) * 12 + (current_date.month - self.Client_data['gst_registered_date'].dt.month)

            # Calculate the number of months since ABN registration
            self.Client_data['ABN_in_Months'] = (current_date.year - self.Client_data['abn_registered_date'].dt.year) * 12 + (current_date.month - self.Client_data['abn_registered_date'].dt.month)

            # Create a new column 'Loan_Amount' as a copy of the 'amount_financed' column
            self.Client_data['Loan_Amount'] = self.Client_data['amount_financed'].copy()

        except KeyError as e:
            raise KeyError(f"Missing column in data: {str(e)}")
        except Exception as e:
            raise Exception(f"An error occurred while creating ABN and GST dates: {str(e)}")

    def dropping_columns(self, column_names=[]):
        """
        Drops irrelevant columns from the dataset.

        Parameters:
        column_names (list): A list of column names to drop from the DataFrame.
        """
        if not isinstance(column_names, list):
            raise TypeError("Column names must be provided as a list.")

        if any([not isinstance(col, str) for col in column_names]):
            raise ValueError("All column names must be strings.")

        missing_columns = [col for col in column_names if col not in self.Client_data.columns]
        if missing_columns:
            raise KeyError(f"The following columns are not in the DataFrame: {missing_columns}")
        try:
            self.Client_data.drop(column_names, axis=1, inplace=True)
        except Exception as e:
            raise Exception(f"An error occurred while dropping columns: {str(e)}")

    def extracting_few_records(self, n_records):
        """
        Extracts the first N records from the dataset.

        Parameters:
        n_records (int): The number of records to extract.

        Returns:
        pd.DataFrame: A DataFrame containing the first N records.
        """
        if not isinstance(n_records, int) or n_records <= 0:
            raise ValueError("n_records must be a positive integer.")

        try:
            return self.Client_data.head(n_records).copy()
        except Exception as e:
            raise Exception(f"An error occurred while extracting records: {str(e)}")

    def converting_df_to_dict(self):
        """
        Converts the DataFrame to a list of dictionaries.
        """
        try:
            self.Data_of_Rule_test = self.Client_data.to_dict(orient="records")
        except Exception as e:
            raise Exception(f"An error occurred while converting the DataFrame to a dictionary: {str(e)}")
