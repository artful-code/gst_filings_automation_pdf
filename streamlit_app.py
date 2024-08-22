import os
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import io
import tempfile
from dateutil.parser import parse
import requests
import zipfile

# Define necessary data structures
known_sources = ['Zoho Books B2B,Export Sales Data', 'Kithab Sales Report', 'Amazon', 'Flipkart - 7(A)(2)', 'Flipkart - 7(B)(2)', 'Meesho','b2b ready to file format','b2cs ready to file format','VS internal format','Amazon B2B','Vyapaar','Jio Mart','pdf data']

known_source_relevenat_columns = {
      'Zoho Books B2B,Export Sales Data': {
          'GST Identification Number (GSTIN)' : 'GSTIN/UIN of Recipient',
          'Customer Name' : 'Receiver Name',
          'Supplier GST Registration Number' : 'GSTIN/UIN of Supplier',
          'Invoice Number' : 'Invoice Number',
          'Invoice Date' : 'Invoice date',
          'Total' : 'Invoice Value',
          'Place of Supply(With State Code)' : 'Place Of Supply',
          'Item Tax %' : 'Rate',
          'SubTotal' : 'Taxable Value',
          'Item Tax Amount' : 'Tax amount',
          'GST Treatment' : 'GST treatment'
      },
      'pdf data': {
          'Invoice Amount' : 'amount',
          'Cgst Tax': 'cgst_amount',
          'Sgst Tax': 'sgst_amount'
      },
      "HSN ready to file": {
          "HSN":"HSN",
          "Description":"Description",
          "UQC":"UQC",
          "Total Quantity":"Total Quantity",
          "Rate":"Rate",
          "Total Value":"Total Value",
          "Taxable Value":"Taxable Value",
          "Integrated Tax Amount":"Integrated Tax Amount",
          "Central Tax Amount":"Central Tax Amount",
          "State/UT Tax Amount":"State/UT Tax Amount",
          "Cess Amount":"Cess Amount"
      },
      "Flipkart HSN": {
          "HSN Number":"HSN",
          "Total Quantity in Nos.":"Total Quantity",
          "Total Value Rs.":"Total Value",
          "Total Taxable Value Rs.":"Taxable Value",
          "IGST Amount Rs.":"Igst Amount",
          "CGST Amount Rs.":"Cgst Amount",
          "SGST Amount Rs.":"Sgst Amount",
          "Cess Rs.":"Cess Amount"
      },
      'Jio Mart': {
          'Seller GSTIN' : 'GSTIN/UIN of Supplier',
          "Customer's Delivery State" : 'Place Of Supply',
          'CGST Rate' : 'Cgst Rate',
          'SGST Rate (or UTGST as applicable)' : 'Sgst Rate',
          'IGST Rate' : 'Igst Rate',
          'Taxable Value (Final Invoice Amount -Taxes)' : 'Taxable Value'
      },
      'Amazon B2B': {
          'Customer Bill To Gstid' : 'GSTIN/UIN of Recipient',
          'Buyer Name' : 'Receiver Name',
          'Seller Gstin' : 'GSTIN/UIN of Supplier',
          'Invoice Number' : 'Invoice Number',
          'Invoice Date' : 'Invoice date',
          'Invoice Amount' : 'Invoice Value',
          'Ship To State' : 'Place Of Supply',
          'Tax Exclusive Gross' : 'Taxable Value',
          'Cgst Rate' : 'Cgst Rate',
          'Sgst Rate' : 'Sgst Rate',
          'Utgst Rate' : 'Utgst Rate',
          'Igst Rate' : 'Igst Rate',
          'Igst Tax': 'Igst Amount',
          'Cgst Tax': 'Cgst Amount',
          'Sgst Tax': 'Sgst Amount',
          'Utgst Tax': 'Ugst Amount'
      },
    #   'Cgst Amount', 'Sgst Amount', 'Igst Amount', 'Ugst Amount',
      'VS internal format': {
          'gstin' : 'GSTIN/UIN of Recipient',
          'Name of Customer' : 'Receiver Name',
          'Invoice No' : 'Invoice Number',
          'Date' : 'Invoice date',
          'Invoice Total (Rs.)' : 'Invoice Value',
          'state' : 'Place Of Supply',
          'Rate of tax (%)' : 'Rate',
          'Invoice Base Amount (Rs.)' : 'Taxable Value',
          'CGST (Rs.)' : 'Cgst Amount',
          'SGST (Rs.)' : 'Sgst Amount',
          'IGST (Rs.)' : 'Igst Amount'
      },
      'b2b ready to file format': {
          'GSTIN/UIN of Recipient' : 'GSTIN/UIN of Recipient',
          'Receiver Name' : 'Receiver Name',
          'Invoice Number' : 'Invoice Number',
          'Invoice date' : 'Invoice date',
          'Invoice Value' : 'Invoice Value',
          'Place Of Supply' : 'Place Of Supply',
          'Rate' : 'Rate',
          'Taxable Value' : 'Taxable Value'
      },
      'b2cs ready to file format': {
          'Place Of Supply' : 'Place Of Supply',
          'Rate' : 'Rate',
          'Taxable Value' : 'Taxable Value'
      },
      'Kithab Sales Report': {
          'GSTIN Number' : 'GSTIN/UIN of Recipient',
          'Customer name' : 'Receiver Name',
          'Invoice Number' : 'Invoice Number',
          'Invoice Date' : 'Invoice date',
          'GST Rate' : 'Rate',
          'Item Price' : 'Taxable Value'
      },
      'Amazon': {
          'Seller Gstin' : 'GSTIN/UIN of Supplier',
          'Invoice Number' : 'Invoice Number',
          'Invoice Date' : 'Invoice date',
          'Invoice Amount' : 'Invoice Value',
          'Ship To State' : 'Place Of Supply',
          'Tax Exclusive Gross' : 'Taxable Value',
          'Total Tax Amount' : 'Tax amount',
          'Cgst Rate' : 'Cgst Rate',
          'Sgst Rate' : 'Sgst Rate',
          'Utgst Rate' : 'Utgst Rate',
          'Igst Rate' : 'Igst Rate',
          'Igst Tax': 'Igst Amount',
          'Cgst Tax': 'Cgst Amount',
          'Sgst Tax': 'Sgst Amount',
          'Utgst Tax': 'Ugst Amount'
      },
      'Meesho': {
          'gstin' : 'GSTIN/UIN of Supplier',
          'end_customer_state_new' : 'Place Of Supply',
          'gst_rate' : 'Rate',
          'tcs_taxable_amount' : 'Taxable Value'
      },
      'Flipkart - 7(A)(2)': {
          'GSTIN' : 'GSTIN/UIN of Supplier',
          'Aggregate Taxable Value Rs.' : 'Taxable Value',
          'CGST %' : 'Cgst Rate',
          'SGST/UT %' : 'Sgst Rate'
      },
      'Flipkart - 7(B)(2)':{
          'GSTIN' : 'GSTIN/UIN of Supplier',
          'Delivered State (PoS)' : 'Place Of Supply',
          'IGST %' : 'Rate',
          'Aggregate Taxable Value Rs.' : 'Taxable Value',
          'IGST Amount Rs.' : 'Tax amount'
      }
  }

state_codes = [
    {
        "State": "Andaman and Nicobar Islands",
        "code": "35-Andaman and Nicobar Islands",
        "code_number": "35"
    },
    {
        "State": "Andhra Pradesh",
        "code": "37-Andhra Pradesh",
        "code_number": "37"
    },
    {
        "State": "Arunachal Pradesh",
        "code": "12-Arunachal Pradesh",
        "code_number": "12"
    },
    {
        "State": "Assam",
        "code": "18-Assam",
        "code_number": "18"
    },
    {
        "State": "Bihar",
        "code": "10-Bihar",
        "code_number": "10"
    },
    {
        "State": "Chandigarh",
        "code": "04-Chandigarh",
        "code_number": "04"
    },
    {
        "State": "Chhattisgarh",
        "code": "22-Chhattisgarh",
        "code_number": "22"
    },
    {
        "State": "Dadra and Nagar Haveli and Daman and Diu",
        "code": "26-Dadra and Nagar Haveli and Daman and Diu",
        "code_number": "26"
    },
    {
        "State": "Daman and Diu",
        "code": "25-Daman and Diu",
        "code_number": "25"
    },
    {
        "State": "Delhi",
        "code": "07-Delhi",
        "code_number": "07"
    },
    {
        "State": "Goa",
        "code": "30-Goa",
        "code_number": "30"
    },
    {
        "State": "Gujarat",
        "code": "24-Gujarat",
        "code_number": "24"
    },
    {
        "State": "Haryana",
        "code": "06-Haryana",
        "code_number": "06"
    },
    {
        "State": "Himachal Pradesh",
        "code": "02-Himachal Pradesh",
        "code_number": "02"
    },
    {
        "State": "Jammu and Kashmir",
        "code": "01-Jammu and Kashmir",
        "code_number": "01"
    },
    {
        "State": "Jharkhand",
        "code": "20-Jharkhand",
        "code_number": "20"
    },
    {
        "State": "Karnataka",
        "code": "29-Karnataka",
        "code_number": "29"
    },
    {
        "State": "Kerala",
        "code": "32-Kerala",
        "code_number": "32"
    },
    {
        "State": "Ladakh",
        "code": "38-Ladakh",
        "code_number": "38"
    },
    {
        "State": "Lakshadweep",
        "code": "31-Lakshadweep",
        "code_number": "31"
    },
    {
        "State": "Madhya Pradesh",
        "code": "23-Madhya Pradesh",
        "code_number": "23"
    },
    {
        "State": "Maharashtra",
        "code": "27-Maharashtra",
        "code_number": "27"
    },
    {
        "State": "Manipur",
        "code": "14-Manipur",
        "code_number": "14"
    },
    {
        "State": "Meghalaya",
        "code": "17-Meghalaya",
        "code_number": "17"
    },
    {
        "State": "Mizoram",
        "code": "15-Mizoram",
        "code_number": "15"
    },
    {
        "State": "Nagaland",
        "code": "13-Nagaland",
        "code_number": "13"
    },
    {
        "State": "Odisha",
        "code": "21-Odisha",
        "code_number": "21"
    },
    {
        "State": "Other Territory",
        "code": "97-Other Territory",
        "code_number": "97"
    },
    {
        "State": "Puducherry",
        "code": "34-Puducherry",
        "code_number": "34"
    },
    {
        "State": "Punjab",
        "code": "03-Punjab",
        "code_number": "03"
    },
    {
        "State": "Rajasthan",
        "code": "08-Rajasthan",
        "code_number": "08"
    },
    {
        "State": "Sikkim",
        "code": "11-Sikkim",
        "code_number": "11"
    },
    {
        "State": "Tamil Nadu",
        "code": "33-Tamil Nadu",
        "code_number": "33"
    },
    {
        "State": "Telangana",
        "code": "36-Telangana",
        "code_number": "36"
    },
    {
        "State": "Tripura",
        "code": "16-Tripura",
        "code_number": "16"
    },
    {
        "State": "Uttar Pradesh",
        "code": "09-Uttar Pradesh",
        "code_number": "09"
    },
    {
        "State": "Uttarakhand",
        "code": "05-Uttarakhand",
        "code_number": "05"
    },
    {
        "State": "West Bengal",
        "code": "19-West Bengal",
        "code_number": "19"
    }
]

state_mis_match_mapping = {
    "AP": "Andhra Pradesh",
    "AN": "Andaman and Nicobar Islands",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CG": "Chattisgarh",
    "CH": "Chandigarh",
    "DN": "Dadra and Nagar Haveli and Daman and Diu",
    "DD": "Dadra and Nagar Haveli and Daman and Diu",
    "DL": "Delhi",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "JK": "Jammu and Kashmir",
    "JH": "Jharkhand",
    "KA": "Karnataka",
    "KL": "Kerala",
    "LA": "Ladakh",
    "LD": "Lakshadweep",
    "MP": "Madhya Pradesh",
    "MH": "Maharashtra",
    "MN": "Manipur",
    "ML": "Meghalaya",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OD": "Odisha",
    "PY": "Pondicherry",
    "PB": "Punjab",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TS": "Telangana",
    "TR": "Tripura",
    "UP": "Uttar Pradesh",
    "UK": "Uttarakhand",
    "WB": "West Bengal",
    "UA": "Uttarakhand",
    "OR": "Odisha",
    "UT": "Uttarakhand",
    "Puducherry": "Pondicherry",
    "The Andaman and Nicobar Islands": "Andaman and Nicobar Islands",
    "Andaman & Nicobar Islands": "Andaman and Nicobar Islands",
    "The Andaman & Nicobar Islands": "Andaman and Nicobar Islands",
    "Orisha": "Odisha",
    "Oddisha": "Odisha",
    "Orrisha": "Odisha",
    "PONDICHERRY": 'Pondicherry',
    "JAMMU & KASHMIR": 'Jammu and Kashmir'

}

needed_columns = [
    'GSTIN/UIN of Recipient', 'Receiver Name', 'GSTIN/UIN of Supplier', 'Invoice Number', 'Invoice date',
    'Invoice Value', 'Place Of Supply', 'Rate', 'Taxable Value', 'Tax amount', 'GST treatment', 'Invoice Type',
    'E-Commerce GSTIN', 'Cess Amount', 'Cgst Rate', 'Sgst Rate', 'Utgst Rate', 'Igst Rate', 'CESS Rate',
    'Cgst Amount', 'Sgst Amount', 'Igst Amount', 'Ugst Amount'
]

# Define necessary functions
def select_columns_from_unknown_source(df, needed_columns, file_name, sheet_name):
    columns = df.columns.tolist()
    available_name_of_needed_columns_dict = {}
    
    st.write("Select the corresponding columns for each needed field:")
    
    for needed_col in needed_columns:
        # Add a "Not Available" option to the list of columns
        options = ["Not Available"] + columns
        
        # Create a selectbox with search functionality for each needed column
        selected_col = st.selectbox(
            f"Select column for '{needed_col}'",
            options,
            key=f"{file_name}_{sheet_name}_select_{needed_col}",
            help=f"Choose the column that corresponds to {needed_col}"
        )
        
        # If a valid column is selected, add it to the dictionary
        if selected_col != "Not Available":
            available_name_of_needed_columns_dict[selected_col] = needed_col
    
    if available_name_of_needed_columns_dict:
        # Select and rename the columns
        df = df[list(available_name_of_needed_columns_dict.keys())]
        df = df.rename(columns=available_name_of_needed_columns_dict)
    else:
        # Create an empty DataFrame if no columns were selected
        df = pd.DataFrame()
    
    # Add missing columns with NaN values
    for col in needed_columns:
        if col not in df.columns:
            df[col] = np.nan
    
    return df

def integers_in_string(s):
    return sum(c.isdigit() for c in s)

def gstin_or_state(df):
    # Check each row and apply the logic
    df['gst_or_state'] = df['Customer GSTIN number/ Place of Supply'].apply(lambda x: 'gst' if integers_in_string(str(x)) > 2 else 'state')
    return df

def select_columns_from_known_source(df, needed_columns, source):
    if source == 'VS internal format':
        # Set the first row as the header
        df = df[2:]  # Take the data less the header row
        df.columns = ['S.No.','Date','Invoice No','Customer GSTIN number/ Place of Supply','Name of Customer','HSN/SAC Code','Invoice Base Amount (Rs.)','Rate of tax (%)','SGST (Rs.)','CGST (Rs.)','IGST (Rs.)','Exempted/Nill rated sales (Rs.)','Invoice Total (Rs.)']

        df = gstin_or_state(df)

        gst_df = df[df['gst_or_state']=='gst'].copy()
        state_df = df[df['gst_or_state']=='state'].copy()

        gst_df['gstin'] = gst_df['Customer GSTIN number/ Place of Supply']
        gst_df['state'] = np.nan

        state_df['state'] = state_df['Customer GSTIN number/ Place of Supply']
        state_df['gstin'] = np.nan

        df = pd.concat([gst_df, state_df], ignore_index=True)

        # HSN ready to file
    
    if source == 'HSN ready to file':

        removed_top_columns = False
        for index, row in df.iterrows():
            if row[0] == 'HSN':
                if index == 0:
                    removed_top_columns = True

        if not removed_top_columns:
            df = df[3:]
            df.columns = ['HSN','Description','UQC','Total Quantity','Rate','Total Value','Taxable Value','Integrated Tax Amount','Central Tax Amount','State/UT Tax Amount','Cess Amount']


    if source == 'b2b ready to file format':

        removed_top_columns = False
        for index, row in df.iterrows():
            if row[0] == 'GSTIN/UIN of Recipient':
                if index == 0:
                    removed_top_columns = True

        if not removed_top_columns:
            df = df[3:]
            df.columns = ['GSTIN/UIN of Recipient', 'Receiver Name',    'Invoice Number',    'Invoice date', 'Invoice Value', 'Place Of Supply',  'Reverse Charge',   'Applicable % of Tax Rate', 'Invoice Type', 'E-Commerce GSTIN', 'Rate', 'Taxable Value' ,'Cess Amount']

    if source == 'b2cs ready to file format':

        removed_top_columns = False
        for index, row in df.iterrows():
            if row[1] == 'Place Of Supply':
                if index == 0:
                    removed_top_columns = True

        if not removed_top_columns:
            df = df[3:]
            df.columns = ['Type',	'Place Of Supply',	'Applicable % of Tax Rate',	'Rate',	'Taxable Value',	'Cess Amount',	'E-Commerce GSTIN']

    available_name_of_needed_columns_dict = known_source_relevenat_columns[source]
    columns_to_keep = list(available_name_of_needed_columns_dict.keys())
    df = df[columns_to_keep]
    df = df.rename(columns=available_name_of_needed_columns_dict)

    for col in needed_columns:
        if col not in df.columns:
            df[col] = np.nan

    return df

def format_place_of_supply(df):
    for index, row in df.iterrows():
        place_of_supply = row['Place Of Supply']

        if place_of_supply in state_mis_match_mapping.keys():
            place_of_supply = state_mis_match_mapping[place_of_supply]

        valid_states = [state['State'] for state in state_codes]
        valid_codes = [state['code_number'] for state in state_codes]
        valid_state_codes = [state['code'] for state in state_codes]

        gstin_value = row['GSTIN/UIN of Recipient']
        gstin_state_code = gstin_value[:2] if isinstance(gstin_value, str) and len(gstin_value)>=2 else None

        if gstin_state_code in valid_codes:
            for state in state_codes:
                if state['code_number'] == gstin_state_code:
                    df.at[index, 'Place Of Supply'] = state['code']
                    break
        elif place_of_supply not in valid_state_codes:
            if isinstance(place_of_supply, str) and place_of_supply.lower() in [state.lower() for state in valid_states]:
                for state in state_codes:
                    if state['State'].lower() == place_of_supply.lower():
                        df.at[index, 'Place Of Supply'] = state['code']
                        break
            elif place_of_supply in valid_codes:
                for state in state_codes:
                    if state['code_number'] == place_of_supply:
                        df.at[index, 'Place Of Supply'] = state['code']
                        break

    return df

def round_to_nearest_zero(value):
    # Check if the difference from the nearest integer is within 0.02
    if abs(value - round(value)) <= 0.02:
        return round(value)
    return value

def fill_missing_values(df):
  # Convert all rate columns to numeric, coercing errors
  df['Invoice Value'] = pd.to_numeric(df['Invoice Value'], errors='coerce').fillna(0)
  df['Taxable Value'] = pd.to_numeric(df['Taxable Value'], errors='coerce').fillna(0)
  df['Tax amount'] = pd.to_numeric(df['Tax amount'], errors='coerce').fillna(0)
  df['Rate'] = pd.to_numeric(df['Rate'], errors='coerce').fillna(0)
  df['Cgst Rate'] = pd.to_numeric(df['Cgst Rate'], errors='coerce').fillna(0)
  df['Sgst Rate'] = pd.to_numeric(df['Sgst Rate'], errors='coerce').fillna(0)
  df['Igst Rate'] = pd.to_numeric(df['Igst Rate'], errors='coerce').fillna(0)
  df['Utgst Rate'] = pd.to_numeric(df['Utgst Rate'], errors='coerce').fillna(0)
  df['Cgst Amount'] = pd.to_numeric(df['Cgst Amount'], errors='coerce').fillna(0)
  df['Sgst Amount'] = pd.to_numeric(df['Sgst Amount'], errors='coerce').fillna(0)
  df['Igst Amount'] = pd.to_numeric(df['Igst Amount'], errors='coerce').fillna(0)
  df['Ugst Amount'] = pd.to_numeric(df['Ugst Amount'], errors='coerce').fillna(0)

  for index, row in df.iterrows():

    invoice_value = 0 if pd.isna(row['Invoice Value']) else row['Invoice Value']
    taxable_value = 0 if pd.isna(row['Taxable Value']) else row['Taxable Value']
    tax_amount = 0 if pd.isna(row['Tax amount']) else row['Tax amount']
    gst_rate = 0 if pd.isna(row['Rate']) else row['Rate']
    cgst_rate = 0 if pd.isna(row['Cgst Rate']) else row['Cgst Rate']
    sgst_rate = 0 if pd.isna(row['Sgst Rate']) else row['Sgst Rate']
    igst_rate = 0 if pd.isna(row['Igst Rate']) else row['Igst Rate']
    utgst_rate = 0 if pd.isna(row['Utgst Rate']) else row['Utgst Rate']
    gst_rate_combined = cgst_rate + sgst_rate + igst_rate + utgst_rate

    cgst_amount = 0 if pd.isna(row['Cgst Amount']) else row['Cgst Amount']
    sgst_amount = 0 if pd.isna(row['Sgst Amount']) else row['Sgst Amount']
    igst_amount = 0 if pd.isna(row['Igst Amount']) else row['Igst Amount']
    ugst_amount = 0 if pd.isna(row['Ugst Amount']) else row['Ugst Amount']
    tax_amount_combined = cgst_amount + sgst_amount + igst_amount + ugst_amount

    if tax_amount == 0 and (tax_amount_combined != 0):
        tax_amount = tax_amount_combined
        df.at[index, 'Tax amount'] = tax_amount

    # Fill gst_rate column & variable from gst_rate_combined if gst_rate is 0
    if gst_rate == 0 and (cgst_rate!=0 or sgst_rate!=0 or igst_rate!=0 or utgst_rate!=0):
      gst_rate = gst_rate_combined
      df.at[index, 'Rate'] = gst_rate

    elif gst_rate == 0 and (cgst_rate==0 and sgst_rate==0 and igst_rate==0 and utgst_rate==0):
      gst_rate = 0
      df.at[index, 'Rate'] = gst_rate

    # Handle the case where gst_rate is like '0.18'
    if gst_rate >= -0.4 and gst_rate <= 0.4:
        gst_rate = gst_rate * 100
        df.at[index, 'Rate'] = gst_rate


    if invoice_value != 0 and gst_rate != 0 and taxable_value == 0:
            taxable_value = invoice_value * 100 / (100 + gst_rate)
            df.at[index, 'Taxable Value'] = taxable_value
            # continue

    elif invoice_value != 0 and gst_rate == 0 and taxable_value != 0:
        tax_amount = invoice_value - taxable_value
        gst_rate = (tax_amount / taxable_value) * 100
        df.at[index, 'Rate'] = gst_rate
        # continue

    elif invoice_value != 0 and gst_rate == 0 and taxable_value == 0 and tax_amount != 0:
        taxable_value = invoice_value - tax_amount
        gst_rate = (tax_amount / taxable_value) * 100
        df.at[index, 'Rate'] = gst_rate
        df.at[index, 'Taxable Value'] = taxable_value
        # continue

    elif invoice_value != 0 and gst_rate == 0 and taxable_value == 0 and gst_rate_combined != 0:
        gst_rate = gst_rate_combined
        taxable_value = invoice_value * 100 / (100 + gst_rate)
        df.at[index, 'Rate'] = gst_rate
        df.at[index, 'Taxable Value'] = taxable_value
        # continue

    if invoice_value == 0 and gst_rate != 0 and taxable_value != 0:
        invoice_value = taxable_value + (taxable_value * gst_rate / 100)
        df.at[index, 'Invoice Value'] = invoice_value
        # continue

    if invoice_value == 0 and gst_rate != 0 and taxable_value == 0 and tax_amount != 0:
        taxable_value = tax_amount * 100 / gst_rate
        invoice_value = taxable_value + tax_amount
        df.at[index, 'Invoice Value'] = invoice_value
        df.at[index, 'Taxable Value'] = taxable_value
        # continue

    elif invoice_value == 0 and gst_rate == 0 and taxable_value != 0 and tax_amount != 0:
        gst_rate = (tax_amount / taxable_value) * 100
        invoice_value = taxable_value + tax_amount
        df.at[index, 'Rate'] = gst_rate
        df.at[index, 'Invoice Value'] = invoice_value
        # continue

    elif invoice_value == 0 and gst_rate == 0 and taxable_value != 0 and tax_amount == 0 and gst_rate_combined != 0:
        gst_rate = gst_rate_combined
        invoice_value = taxable_value + (taxable_value * gst_rate / 100)
        df.at[index, 'Rate'] = gst_rate
        df.at[index, 'Invoice Value'] = invoice_value
        continue

    elif invoice_value == 0 and gst_rate == 0 and taxable_value == 0 and tax_amount != 0 and gst_rate_combined != 0:
        gst_rate = gst_rate_combined
        taxable_value = tax_amount * 100 / gst_rate
        invoice_value = taxable_value + tax_amount
        df.at[index, 'Rate'] = gst_rate
        df.at[index, 'Taxable Value'] = taxable_value
        df.at[index, 'Invoice Value'] = invoice_value
        # continue

    if tax_amount == 0 and invoice_value != 0 and taxable_value != 0:
        tax_amount = invoice_value - taxable_value
        df.at[index, 'Tax amount'] = tax_amount

    gst_rate = round_to_nearest_zero(gst_rate)

    df.at[index, 'Rate'] = gst_rate

  return df

def create_place_of_origin_column(df):
    df['place_of_origin'] = np.nan

    for index, row in df.iterrows():
        supplier_gstin = row['GSTIN/UIN of Supplier']

        if pd.notna(supplier_gstin) and isinstance(supplier_gstin, str):
            if len(supplier_gstin) >= 2:
                supplier_state_code = supplier_gstin[:2]
                for state in state_codes:
                    if state['code_number'] == supplier_state_code:
                        df.at[index, 'place_of_origin'] = state['code']
                        break

    return df

def fill_place_of_supply_with_place_of_origin(df):
    for index, row in df.iterrows():
        if pd.isna(row['Place Of Supply']):
            df.at[index, 'Place Of Supply'] = row['place_of_origin']
    return df

def categorise_transactions(df):
    df['transaction_type'] = np.nan

    for index, row in df.iterrows():
        gstin_of_recipient = row['GSTIN/UIN of Recipient']
        place_of_supply = row['Place Of Supply']
        invoice_value = row['Invoice Value']
        place_of_origin = row['place_of_origin']
        gst_treatment = row['GST treatment']

        if gst_treatment != 'overseas':
            if pd.notna(gstin_of_recipient):
                df.at[index, 'transaction_type'] = 'b2b'
            elif place_of_supply != place_of_origin and invoice_value > 250000:
                df.at[index, 'transaction_type'] = 'b2cl'
            else:
                df.at[index, 'transaction_type'] = 'b2cs'

    return df

def create_b2b_dataframe(df):
    b2b = df[df['transaction_type'] == 'b2b']
    b2b_columns_needed = ['GSTIN/UIN of Recipient', 'Receiver Name', 'Invoice Number', 'Invoice date',
                          'Invoice Value', 'Place Of Supply', 'Reverse Charge', 'Applicable % of Tax Rate',
                          'Invoice Type', 'E-Commerce GSTIN', 'Rate', 'Taxable Value', 'Cess Amount']
    
    # Ensure all needed columns exist
    for col in b2b_columns_needed:
        if col not in b2b.columns:
            b2b[col] = np.nan
    
    return b2b[b2b_columns_needed]

def create_b2cs_dataframe(df):
    b2cs = df[df['transaction_type'] == 'b2cs'].copy()
    b2cs['Type'] = 'b2cs'
    b2cs['Applicable % of Tax Rate'] = np.nan
    b2cs['E-Commerce GSTIN'] = np.nan
    
    # Now perform the aggregation on the filtered data
    b2cs = b2cs.groupby(['Place Of Supply', 'Rate'])[['Taxable Value', 'Cess Amount']].sum().reset_index()
    
    b2cs_columns_needed = ['Type', 'Place Of Supply', 'Applicable % of Tax Rate', 'Rate', 'Taxable Value', 'Cess Amount', 'E-Commerce GSTIN']
    for col in b2cs_columns_needed:
        if col not in b2cs.columns:
            b2cs[col] = np.nan

    b2cs['Type'] = 'OE'

    b2cs = b2cs[b2cs['Taxable Value']!=0]
    
    return b2cs[b2cs_columns_needed]

def create_b2cl_dataframe(df):
    b2cl = df[df['transaction_type'] == 'b2cl']
    b2cl_columns_needed = ['Invoice Number', 'Invoice date', 'Invoice Value', 'Place Of Supply',
                           'Applicable % of Tax Rate', 'Rate', 'Taxable Value', 'Cess Amount', 'E-Commerce GSTIN']
    
    # Ensure all needed columns exist
    for col in b2cl_columns_needed:
        if col not in b2cl.columns:
            b2cl[col] = np.nan
    
    return b2cl[b2cl_columns_needed]

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

#convert to excel
def convert_csv_to_excel(csv_file):
    df = pd.read_csv(csv_file)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def process_meesho_files(uploaded_files):
    file_names = [file.name for file in uploaded_files]
    
    if 'ForwardReports.xlsx' in file_names and 'Reverse.xlsx' in file_names:
        forward_df = pd.read_excel([file for file in uploaded_files if file.name == 'ForwardReports.xlsx'][0])
        reverse_df = pd.read_excel([file for file in uploaded_files if file.name == 'Reverse.xlsx'][0])

        columns_to_keep = ['gst_rate', 'tcs_taxable_amount', 'end_customer_state_new','gstin']
        forward_df = forward_df[columns_to_keep]
        reverse_df = reverse_df[columns_to_keep]

        reverse_df['tcs_taxable_amount'] *= -1

        combined_df = pd.concat([forward_df, reverse_df], ignore_index=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            combined_df.to_excel(tmp.name, index=False, engine='openpyxl')
            tmp_path = tmp.name

        with open(tmp_path, 'rb') as file:
            output = io.BytesIO(file.read())

        os.unlink(tmp_path)

        new_uploaded_files = [file for file in uploaded_files if file.name not in ['ForwardReports.xlsx', 'Reverse.xlsx']]
        new_uploaded_files.append(('MeeshoForwardReverse.xlsx', output))

        return new_uploaded_files
    
    return uploaded_files

def fill_missing_supplier_gstins(df, unique_counter_for_key_names, sheet):
    # Handle edge case: remove rows where all columns are empty
    df = df.dropna(how='all')

    if 'GSTIN/UIN of Supplier' not in df.columns:
        # All rows have missing GSTIN
        supplier_gstin = st.text_input(
            "All rows are missing supplier GSTIN. Please enter the GSTIN of the supplier:",
            key=f"missing_gstin_column_{unique_counter_for_key_names}_{sheet}"
        )

        if supplier_gstin:
            df['GSTIN/UIN of Supplier'] = supplier_gstin
            return df
        else:
            st.error("Please enter a valid GSTIN for the supplier.")
            st.stop()

    else:
        # Check for rows with missing GSTIN
        df_with_no_gstin = df[df['GSTIN/UIN of Supplier'].isna()]

        if len(df_with_no_gstin) == 0:
            return df  # No missing GSTINs, return original dataframe

        elif len(df) == len(df_with_no_gstin):
            # All rows have missing GSTIN
            supplier_gstin = st.text_input(
                "All rows are missing supplier GSTIN. Please enter the GSTIN of the supplier:",
                key=f"all_missing_gstin_{unique_counter_for_key_names}_{sheet}"
            )

            if supplier_gstin:
                df['GSTIN/UIN of Supplier'] = supplier_gstin
                return df
            else:
                st.error("Please enter a valid GSTIN for the supplier.")
                st.stop()

        else:
            # Some rows have missing GSTIN
            non_nan_gstins = df['GSTIN/UIN of Supplier'].dropna().unique()
            
            if len(non_nan_gstins) == 1:
                # Only one unique non-NaN GSTIN
                df['GSTIN/UIN of Supplier'].fillna(non_nan_gstins[0], inplace=True)
                return df
            else:
                # Multiple unique non-NaN GSTINs
                nan_count = len(df_with_no_gstin)
                st.error(f"{nan_count} transactions do not have Supplier's GSTIN and multiple GSTINs are presnt in other transactions. Please fill and re-upload.")
                st.stop()


def process_pdf_files(uploaded_files):
    pdf_files = [file for file in uploaded_files if file.name.lower().endswith('.pdf')]
    other_files = [file for file in uploaded_files if not file.name.lower().endswith('.pdf')]
    
    if not pdf_files:
        return uploaded_files

    url = 'https://ml.vakilsearch.com/llm-doc/extract-invoice-info-test/'
    headers = {
        'Authorization': 'Bearer UJ6AzYtILSVKOiSDIsASVzUofvvX2KIK6kTEP4dLV1XQZvhdkw2lHLv8zO8At6XgJYm7d'
    }

    processed_dataframes = []
    failed_pdfs = []

    total_pdfs = len(pdf_files)
    processed_pdfs = 0
    successful_pdfs = 0

    # Create placeholders for the counters
    counter_placeholder = st.empty()
    progress_bar = st.progress(0)

    for pdf_file in pdf_files:
        response = requests.post(
            url,
            headers=headers,
            files={'document': pdf_file}
        )

        processed_pdfs += 1

        if response.status_code == 200:
            data = response.json()
            
            invoice_data = {
                "invoice_number": data.get("invoice_number"),
                "invoice_date": data.get("invoice_date"),
                "due_date": data.get("due_date"),
                "terms": data.get("terms"),
                "place_of_supply": data.get("place_of_supply"),
                "bill_to_name": data.get("bill_to", {}).get("name"),
                "bill_to_address": data.get("bill_to", {}).get("address"),
                "sub_total": data.get("totals", {}).get("sub_total"),
                "cgst_total": data.get("totals", {}).get("cgst_total"),
                "sgst_total": data.get("totals", {}).get("sgst_total"),
                "rounding": data.get("totals", {}).get("rounding"),
                "total": data.get("totals", {}).get("total"),
                "balance_due": data.get("totals", {}).get("balance_due"),
                "company_name": data.get("company_details", {}).get("name"),
                "company_address": data.get("company_details", {}).get("address"),
                "company_gstin": data.get("company_details", {}).get("gstin"),
            }

            invoice_df = pd.DataFrame([invoice_data])
            items_df = pd.json_normalize(data, 'items')

            if check_accuracy(invoice_df, items_df):
                processed_dataframes.append(items_df)
                successful_pdfs += 1
            else:
                failed_pdfs.append(pdf_file)
        else:
            failed_pdfs.append(pdf_file)

        # Update the counter and progress bar
        counter_placeholder.text(f"Processed: {processed_pdfs}/{total_pdfs} | Successful: {successful_pdfs} | Failed: {len(failed_pdfs)}")
        progress_bar.progress(processed_pdfs / total_pdfs)

    if processed_dataframes:
        final_df = pd.concat(processed_dataframes, ignore_index=True)
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False)
        excel_buffer.seek(0)
        
        new_file = io.BytesIO(excel_buffer.getvalue())
        new_file.name = "processed_pdf_data.xlsx"
        other_files.append(new_file)

    if failed_pdfs:
        st.warning(f"{len(failed_pdfs)} PDFs failed processing. Click below to download them.")
        
        # Create a BytesIO object to hold the ZIP file
        zip_buffer = io.BytesIO()
        
        # Create a ZipFile object
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, pdf in enumerate(failed_pdfs):
                # Write each failed PDF to the ZIP file with a unique name
                zip_file.writestr(f"failed_pdf_{i+1}.pdf", pdf.getvalue())
        
        # Reset the buffer's position to the beginning
        zip_buffer.seek(0)
        
        # Offer the ZIP file for download
        st.download_button(
            label="Download Failed PDFs",
            data=zip_buffer,
            file_name="failed_pdfs.zip",
            mime="application/zip"
        )

    # Final update to the counter
    counter_placeholder.text(f"Final Results - Processed: {processed_pdfs}/{total_pdfs} | Successful: {successful_pdfs} | Failed: {len(failed_pdfs)}")
    progress_bar.progress(1.0)

    return other_files

def check_accuracy(df_invoice, df_items):
    df_items['item_total'] = round(df_items['quantity'] * df_items['rate'], 2)
    sub_total_amount = round(df_items['item_total'].sum(), 2)
    sum_total_amount = round(df_items['amount'].sum(), 2)
    sum_cgst_amount = round(df_items['cgst_amount'].sum(), 2)
    sum_sgst_amount = round(df_items['sgst_amount'].sum(), 2)
    
    invoice_total = round(df_invoice.at[0, 'total'], 2)
    rounding_adjustment = round(df_invoice.at[0, 'rounding'], 2)
    sub_total = round(df_invoice.at[0, 'sub_total'], 2)
    cgst_total = round(df_invoice.at[0, 'cgst_total'], 2)
    sgst_total = round(df_invoice.at[0, 'sgst_total'], 2)
    
    invoice_total_check = round(abs((invoice_total - rounding_adjustment) - sum_total_amount), 2) <= 0.01
    sub_total_check = round(abs(sub_total - sub_total_amount), 2) <= 0.01
    cgst_total_check = round(abs(cgst_total - sum_cgst_amount), 2) <= 0.01
    sgst_total_check = round(abs(sgst_total - sum_sgst_amount), 2) <= 0.01
    
    return all([invoice_total_check, sub_total_check, cgst_total_check, sgst_total_check])


# Streamlit app
def main():
    st.title("GST FILINGS AUTOMATION")
    
    uploaded_files = st.file_uploader("Choose Excel, CSV, or PDF files", accept_multiple_files=True, type=['xlsx', 'xls', 'csv', 'pdf'])

    if uploaded_files:
        uploaded_files = process_pdf_files(uploaded_files)
        uploaded_files = process_meesho_files(uploaded_files)
    
    # if uploaded_files:
    #     uploaded_files = process_meesho_files(uploaded_files)

        processed_files = []
        for file in uploaded_files:
            if isinstance(file, tuple):  # Combined Meesho file
                file_name, file_content = file
                file_obj = io.BytesIO(file_content.getvalue())
                file_obj.name = file_name
                processed_files.append(file_obj)
            else:  # Original UploadedFile
                if file.name.endswith('.csv'):
                    processed_data = convert_csv_to_excel(file)
                    processed_file = io.BytesIO(processed_data)
                    processed_file.name = file.name.replace('.csv', '.xlsx')
                    processed_files.append(processed_file)
                else:
                    processed_files.append(file)

        all_dataframes = []
        for uploaded_file in processed_files:
            st.write(f"Processing: {uploaded_file.name}")
            
            if uploaded_file.name.endswith(('.xlsx', '.xls')):
                excel_file = pd.ExcelFile(uploaded_file)
                sheet_names = excel_file.sheet_names
                selected_sheets = st.multiselect(f"Select relevant sheets from {uploaded_file.name}", sheet_names)

                unique_counter_for_key_names = 0
                
                for sheet in selected_sheets:
                    unique_counter_for_key_names += 1
                    df = excel_file.parse(sheet)
                    is_known_source = st.checkbox(f"Is {sheet} from a known format?", key=f"{uploaded_file.name}_{sheet}_known", value=True)
                    
                    if is_known_source:
                        source = st.selectbox("Select the format", known_sources, key=f"{uploaded_file.name}_{sheet}_source")
                        df = select_columns_from_known_source(df, needed_columns, source)
                        df = fill_missing_supplier_gstins(df, unique_counter_for_key_names, sheet)
                    else:
                        df = select_columns_from_unknown_source(df, needed_columns, uploaded_file.name, sheet)
                        df = fill_missing_supplier_gstins(df, unique_counter_for_key_names, sheet)
                    
                    if not df.empty:
                        df = format_place_of_supply(df)

                        df = fill_missing_values(df)
                        df = create_place_of_origin_column(df)
                        df = fill_place_of_supply_with_place_of_origin(df)

                        taxable_value = df['Taxable Value'].sum()
                        tax_amount = df['Tax amount'].sum()
                        igst_tax_amount = df[df['Place Of Supply'] != df['place_of_origin']]['Tax amount'].sum()
                        cgst_tax_amount = df[df['Place Of Supply'] == df['place_of_origin']]['Tax amount'].sum()/2
                        sgst_tax_amount = df[df['Place Of Supply'] == df['place_of_origin']]['Tax amount'].sum()/2

                        st.title(f'Summary of {sheet} for TCS')
                        # Assuming the variables are already calculated
                        summary_data = {
                            "Taxable Value": [taxable_value],
                            "IGST Amount": [igst_tax_amount],
                            "CGST Amount": [cgst_tax_amount],
                            "SGST Amount": [sgst_tax_amount]
                        }

                        # Convert the data into a DataFrame
                        summary_df = pd.DataFrame(summary_data)
                        st.table(summary_df)

                        all_dataframes.append(df)

        if all_dataframes:
            main_df = pd.concat(all_dataframes)
            main_df.reset_index(drop=True, inplace=True)

            # print(main_df)
            # st.write(main_df)
            # print('main_df')
            
            # customer_state_code = st.selectbox("Select the state code of the supplier", 
            #                                    [state['code'] for state in state_codes])
            
            # main_df = fill_missing_values(main_df)
            # main_df = create_place_of_origin_column(main_df, customer_state_code)
            # main_df = fill_place_of_supply_with_place_of_origin(main_df)
            main_df = categorise_transactions(main_df)


            # Function to parse dates with mixed formats
            def parse_date(date, user_month):
                if pd.isna(date):
                    return None  # Return None for missing values
                try:
                    parsed_date = parse(str(date), dayfirst=False)  # Parse assuming month/day/year
                except ValueError:
                    parsed_date = parse(str(date), dayfirst=True)   # Parse assuming day/month/year
                
                if parsed_date.month == user_month:
                    return parsed_date
                else:
                    # Swap day and month if the user input doesn't match
                    try:
                        corrected_date = parsed_date.replace(day=parsed_date.month, month=user_month)
                        return corrected_date
                    except ValueError:
                        return None


            # Dropdown to select the month
            month_names = ["January", "February", "March", "April", "May", "June", 
                        "July", "August", "September", "October", "November", "December"]
            current_month = pd.Timestamp.now().month
            previous_month = (current_month - 2) % 12  # Adjusted to select the previous month by default
            user_month = st.selectbox("Select the month of the dates in your data:", month_names, index=previous_month)
            user_month_index = month_names.index(user_month) + 1  # Convert month name to month number

            # Apply the function to the 'Invoice Date' column
            main_df['Invoice date'] = main_df['Invoice date'].apply(lambda x: parse_date(x, user_month_index))

            # Change the format to '01-Jul-2024', handling NaT values gracefully
            main_df['Invoice date'] = main_df['Invoice date'].apply(lambda x: x.strftime('%d-%b-%y') if pd.notna(x) else None)

            main_df['GSTIN/UIN of Supplier'].fillna('supplier gstin not available', inplace=True)

            main_df['GSTIN/UIN of Supplier'] = main_df['GSTIN/UIN of Supplier'].astype(str).apply(lambda x: x[:15])
            main_df['GSTIN/UIN of Recipient'] = main_df['GSTIN/UIN of Recipient'].astype(str).apply(lambda x: x[:15])

            main_df['Reverse Charge'] = 'N'
            main_df['Invoice Type'] = 'Regular B2B'

            unique_gstins = main_df['GSTIN/UIN of Supplier'].unique()
            
            for gstin in unique_gstins:
                st.write(f"### Summary for GSTIN: {gstin}")
                gstin_df = main_df[main_df['GSTIN/UIN of Supplier'] == gstin]
                
                b2b = create_b2b_dataframe(gstin_df)
                b2cs = create_b2cs_dataframe(gstin_df)
                b2cl = create_b2cl_dataframe(gstin_df)
                
                if not b2b.empty:
                    st.download_button(
                        label=f"Download B2B Output for {gstin}",
                        data=convert_df_to_csv(b2b),
                        file_name=f"b2b_output_{gstin}.csv",
                        mime="text/csv",
                    )
                else:
                    st.write(f"No B2B transactions to download for GSTIN: {gstin}.")
                
                if not b2cs.empty:
                    st.download_button(
                        label=f"Download B2CS Output for {gstin}",
                        data=convert_df_to_csv(b2cs),
                        file_name=f"b2cs_output_{gstin}.csv",
                        mime="text/csv",
                    )
                else:
                    st.write(f"No B2CS transactions to download for GSTIN: {gstin}.")
                
                if not b2cl.empty:
                    st.download_button(
                        label=f"Download B2CL Output for {gstin}",
                        data=convert_df_to_csv(b2cl),
                        file_name=f"b2cl_output_{gstin}.csv",
                        mime="text/csv",
                    )
                else:
                    st.write(f"No B2CL transactions to download for GSTIN: {gstin}.")
        else:
            st.error("No valid data was processed from the uploaded files. Please check your input and try again.")
    else:
        st.write("Please upload Excel files to process.")

if __name__ == "__main__":
    main()
