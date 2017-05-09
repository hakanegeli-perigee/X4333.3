import pandas as pd
import os.path


class IppsData:

    def __init__(self):
        # in case if we want to store the data in a separate directory
        self._datafile_dir = ""

        # internal property which holds the IPPS DataFrame
        self._data = None

    def get_data(self):
        """
        This method loads the IPPS data from a CSV file and adds the Region and Urban columns
        
        :return: DataFrame containing IPPS data
        """

        ipps_data = self.__load_ipps_data()
        zipcode_data = self.__get_zip_code_data()
        self._data = self.add_zip_code_data_to_ipps(ipps_data, zipcode_data)
        return self._data

    def __load_ipps_data(self):
        """
        This method reads the IPPS data from a CSV file
        
        :return: Raw IPPS DataFrame
        """

        if not os.path.exists(os.path.join(self._datafile_dir, "IPPS_Provider_Data.csv")):
            raise Exception("Missing IPPS_Provider_Data.csv file!")

        headers = ['DRG_Definition', 'Provider_Id', 'Provider_Name', 'Provider_Street_Address',
                   'Provider_City', 'Provider_State', 'Provider_Zip_Code',
                   'Hospital_Referral_Region_Description', 'Total_Discharges',
                   'Average_Covered_Charges', 'Average_Total_Payments', 'Average_Medicare_Payments']
        return pd.read_csv(os.path.join(self._datafile_dir, "IPPS_Provider_Data.csv"),
                           header=0,
                           names=headers,
                           converters={'Average_Covered_Charges': lambda x: float(x.replace('$', '')),
                                       'Average_Total_Payments': lambda x: float(x.replace('$', '')),
                                       'Average_Medicare_Payments': lambda x: float(x.replace('$', ''))})

    def __get_zip_code_data(self):
        """
        This method reads zip code and MSA and the US Region data from a CSV file and creates a ZipCode DataFrame 
        
        :return: ZipCode DataFrame 
        """

        # 5 digit zip code, city, state, zip, Metropolitan Statistical Area (MSA), latitude, longitude, etc.
        zip_codes = pd.read_csv(os.path.join(self._datafile_dir, "5DigitZipcodes.csv"))

        # Metropolitan Statistical Area Code to Metropolitan Statistical Area Name mapping
        msa_codes = pd.read_csv(os.path.join(self._datafile_dir, "MSACodes.csv"))

        # State, division and region mapping
        us_regions = pd.read_csv(os.path.join(self._datafile_dir, "USRegions.csv"))

        # create a state to region mapping
        state_to_region = {state_abbr: region for state_abbr, region in us_regions[["State_Abbr", "Region"]].values}
        zip_codes["Region"] = zip_codes["State_Abbr"].map(state_to_region)

        # create MSA (Metropolitan Statistical Area) code to MSA Name mapping
        msa_code_to_msa_name = {msa_code: msa_name for msa_code, msa_name in msa_codes[["MSA_Code", "MSA_Name"]].values}
        zip_codes["MSA_Name"] = zip_codes["MSA_Code"].map(msa_code_to_msa_name)

        # zip code data contains entries for zip codes with alternate city names
        # and we need to build a unique list of zip codes
        unique_zip_codes = zip_codes[["Zip_Code", "State_Abbr", "Region", "MSA_Code", "MSA_Name"]].drop_duplicates()

        # remove any zip code entry without region, such as PR, GU, military, etc.
        unique_zip_codes = unique_zip_codes[pd.isnull(unique_zip_codes.Region) == False]

        # crate an Urban column based on the MSACode.
        # if the MSA Code is 0 then rural otherwise urban
        unique_zip_codes["Urban"] = ["urban" if msa_code > 0 else "rural" for msa_code in unique_zip_codes.MSA_Code.values]

        # return only the columns we need
        unique_zip_codes = unique_zip_codes[["Zip_Code", "State_Abbr", "Region", "Urban", "MSA_Name"]]

        return unique_zip_codes

    def add_zip_code_data_to_ipps(self, ipps, zipcode):
        """
        This method merges IPPS DataFrame and the ZipCode DataFrame into a single DataFrame
        
        :param ipps: IPPS DataFrame 
        :param zipcode: ZipCode DataFrame
        :return: Merged IPPS DataFrame
        """

        # we will join the 'Provider_Zip_Code' column from the ipps and the 'Zip_Code' field from the zipcode
        return pd.merge(ipps, zipcode, left_on='Provider_Zip_Code', right_on='Zip_Code', how='left')
