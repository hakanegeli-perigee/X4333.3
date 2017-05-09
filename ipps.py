import pandas as pd
import os.path


class IppsData:

    def __init__(self):
        # in case if we want to store the data in a separate directory
        self._datafile_dir = ""
        self._data = None

    def get_data(self):
        ipps_data = self.__load_ipps_data()

        zipcode_data = self.__get_zip_code_data()

        self._data = self.add_zip_code_data_to_ipps(ipps_data, zipcode_data)

        return self._data

    def __load_ipps_data(self):
        if not os.path.exists(os.path.join(self._datafile_dir, "IPPS_Provider_Data.csv")):
            raise Exception("Missing IPPS_Provider_Data.csv file!")

        return pd.read_csv(os.path.join(self._datafile_dir, "IPPS_Provider_Data.csv"))

    def reload_ipps_data(self):
        self.__load_ipps_data()

    def __get_zip_code_data(self):
        # 5 digit zip codes, city, state, zip, Metropolitan Statistical Area (MSA), latitude, longitude, etc.
        zip_codes = pd.read_csv(os.path.join(self._datafile_dir, "5DigitZipcodes.csv"))

        # Metropolitan Statistical Area Code to Metropolitan Statistical Area Name information
        msa_codes = pd.read_csv(os.path.join(self._datafile_dir, "MSACodes.csv"))

        # State, division and region information
        us_regions = pd.read_csv(os.path.join(self._datafile_dir, "USRegions.csv"))

        # create a state to region dictionary for mapping
        state_to_region = {state_abbr: region for state_abbr, region in us_regions[["StateAbbr", "Region"]].values}

        # map regions to zip code dataframe
        zip_codes["Region"] = zip_codes["StateAbbr"].map(state_to_region)

        # create MSA (Metropolitan Statistical Area) code to MSA name (aka, Metropolitan Area Name)
        msa_code_to_msa_name = {msa_code: msa_name for msa_code, msa_name in msa_codes[["MSACode", "MSAName"]].values}
        zip_codes["MSAName"] = zip_codes["MSACode"].map(msa_code_to_msa_name)

        # zip code data contains entries for zip codes with alternate city names.
        # we need to build a unique list of zip code, states and region for mapping to ipps data
        unique_zip_codes = zip_codes[["ZIPCode", "StateAbbr", "Region", "MSACode", "MSAName"]].drop_duplicates()

        # remove any zip code entry without region, such as PR, GU, military, etc.
        unique_zip_codes = unique_zip_codes[pd.isnull(unique_zip_codes.Region) == False]

        # crate an Urban column based on the MSACode. If the code is 0 then rural otherwise urban
        unique_zip_codes["Urban"] = ['urban' if msa_code > 0 else 'rural' for msa_code in unique_zip_codes.MSACode.values]

        # we no longer need the MSACode and we'll return only the columns we need
        unique_zip_codes = unique_zip_codes[["ZIPCode", "StateAbbr", "Region", "Urban", "MSAName"]]

        # rename the 'MSAName' to 'UrbanAreaName' for clarity and human readability (optional)
        unique_zip_codes.columns = ["ZIPCode", "StateAbbr", "Region", "Urban", "UrbanAreaName"]

        return unique_zip_codes

    def add_zip_code_data_to_ipps(self, ipps, zipcode):
        # we will join the 'Provider Zip Code' column from the ipps and the 'ZIPCode' field from the zipcode_data and add the Region, Urban, Urban Name columns to ipps
        return pd.merge(ipps, zipcode, left_on='Provider Zip Code', right_on='ZIPCode', how='left')
