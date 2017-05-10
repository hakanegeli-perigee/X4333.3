import pandas as pd
import os.path


class IppsData:


    """
    DESCRIPTION
    
    This object contains the Prospective Payment System Provider Summary (IPPS) data.
    
    
    USAGE
    
    from ipps import IppsData
    
    Call the .load() method to load the data once
    ipps_data = IppsData()
    ipps_data.load()
    
    Call the .data property to access the loaded DataFrame
    ipps_data.data
    
    """
    def __init__(self):
        # in case if we want to store the data in a separate directory
        self._datafile_dir = ""

        # internal property which holds the IPPS DataFrame
        self._data = None

    @property
    def data(self):
        """
        This property returns the loaded the IPPS DataFrame

        :return: DataFrame containing IPPS data
        """
        return self._data

    def load(self):
        """
        This method loads the IPPS data from a CSV file and adds the Region and Urban columns.
        Loaded DataFrame can be accessed using the .data property
        
        :return: None
        """
        data = self.__load_ipps_data()
        data["DRG_Code"] = [int(drg_definition.split(" - ", 1)[0]) for drg_definition in data.DRG_Definition.values]
        zipcode_data = self.__get_zip_code_data()
        data = self.__add_zip_code_data_to_ipps(data, zipcode_data)
        del(data["Zip_Code"])
        del (data["State_Abbr"])
        self._data = data

    def __load_ipps_data(self):
        """
        This private method reads the IPPS data from a CSV file
        
        :return: Raw IPPS DataFrame
        """
        # check if the provider data file exists, raise an expection if the file is not found
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
        This private method reads zip code and MSA and the US Region data from a CSV file and creates a Zip Code DataFrame 
        
        :return: Zip Code DataFrame 
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

    def __add_zip_code_data_to_ipps(self, ipps, zipcode):
        """
        This private method merges IPPS and the Zip Code DataFrames into a single DataFrame
        
        :param ipps: IPPS DataFrame which contains the DRG Codes, Provider and Payment data
        :param zipcode: Zip Code DataFrame which contains the zip codes, regions and MSA information
        :return: Merged IPPS DataFrame
        """
        # we will join the 'Provider_Zip_Code' column from the ipps and the 'Zip_Code' field from the zipcode
        return pd.merge(ipps, zipcode, left_on='Provider_Zip_Code', right_on='Zip_Code', how='left')
