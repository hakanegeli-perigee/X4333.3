import pandas as pd

def load_ipps_data():
    return pd.read_csv("data/IPPS_Provider_Data.csv")

def get_zipcode_data():
    # 5 digit zip codes city, state, zip, Metropolitan Statistical Area (MSA), latitude, longitude, etc.
    zip_codes = pd.read_csv("data/5DigitZipcodes.csv")

    # Metropolitan Statistical Area Code to Metropolitan Statistical Area Name information
    msa_codes = pd.read_csv("data/MSACodes.csv")

    # State, division and region information
    us_regions = pd.read_csv("data/USRegions.csv")

    # create a state to region dictionary for mapping
    state_to_region = {state_abbr: region for state_abbr, region in us_regions[["StateAbbr", "Region"]].values}

    # map regions to zipcodes dataframe
    zip_codes["Region"] = zip_codes["StateAbbr"].map(state_to_region)

    # create MSA (Metropolitan Statistical Area) code to MSA name (aka, Metropolitan Area Name)
    msa_code_to_msa_name = {msa_code: msa_name for msa_code, msa_name in msa_codes[["MSACode", "MSAName"]].values}
    zip_codes["MSAName"] = zip_codes["MSACode"].map(msa_code_to_msa_name)

    # zipcode data contains entries for zipcodes with alternate city names.
    # we need to build a unique list of zipcode, states and region for mapping to ipps data
    unique_zipcodes = zip_codes[["ZIPCode", "StateAbbr", "Region", "MSACode", "MSAName"]].drop_duplicates()

    # remove any zipcode entries witout region, such as PR, GU, military, etc.
    unique_zipcodes = unique_zipcodes[pd.isnull(unique_zipcodes.Region)==False] #.Region.unique()

    # crate an Urban column based on the MSACode. If the code is 0 then rural otherwise urban
    unique_zipcodes["Urban"] = ['urban' if msa_code > 0 else 'rural' for msa_code in unique_zipcodes.MSACode.values]
    
    # we no longer need the MSACode and we'll return only the columns we need
    unique_zipcodes = unique_zipcodes[["ZIPCode", "StateAbbr", "Region", "Urban", "MSAName"]]

    # rename the 'MSAName' to 'UrbanAreaName' for clarity and human readility (optional)
    unique_zipcodes.columns = ["ZIPCode", "StateAbbr", "Region", "Urban", "UrbanAreaName"]

    return unique_zipcodes

def add_zipcode_data_to_ipps(ipps, zipcode):
    # we will join the 'Provider Zip Code' column from the ipps and the 'ZIPCode' field from the zipcode_data and add the Region, Urban, Urban Name columns to ipps
    return pd.merge(ipps, zipcode, left_on='Provider Zip Code', right_on='ZIPCode', how='left')

def main():
    ipps_data = load_ipps_data()
    zipcode_data = get_zipcode_data()

    ipps_data = add_zipcode_data_to_ipps(ipps_data, zipcode_data)
    ipps_data.to_csv("data/IPPS_Provider_Data_Merged.csv")

if __name__ == "__main__":
    main()