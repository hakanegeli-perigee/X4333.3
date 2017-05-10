# -*- coding: utf-8 -*-
"""
Spyder Editor
Andrew Munro
Group Project
DRGtoMDC.py

The DRGtoMDC class takes the inputs of Diagnosis-Related Groups (DRG) codes, 
and reassigns them to Major Diagnostic Categories (MDC)

This class also splits the DRG code-dash-description column to create the
DRG code, DRG Description, MDC code, and MDC description

MDC tighter groupings are assigned at the head of the remap function (e.g. )

.
"""

import pandas as pd
import os.path


class DRGtoMDC:
    def __init__(self):
        # in case if we want to store the data in a separate directory
        self._datafile_dir = ""

        # internal property which holds the IPPS DataFrame
        self._data = None

    # def load(self):
    #     """
    #     This method gets the DRG column and adds the MDC column to the CSV file
    #     :return: None
    #     """
    #     self.__load_drg_data()
    #
    # def __load_drg_data(self):
    #     """
    #     This private method reads the IPPS data from a CSV file (provided by Hakan Egeli)
    #
    #     :return: Raw IPPS DataFrame
    #     """
    #     # check if the provider data file exists, raise an expection if the file is not found
    #     if not os.path.exists(os.path.join(self._datafile_dir, "IPPS_Provider_Data.csv")):
    #         raise Exception("Missing IPPS_Provider_Data.csv file!")
    #     headers = ['DRG_Definition', 'Provider_Id', 'Provider_Name', 'Provider_Street_Address',
    #                'Provider_City', 'Provider_State', 'Provider_Zip_Code',
    #                'Hospital_Referral_Region_Description', 'Total_Discharges',
    #                'Average_Covered_Charges', 'Average_Total_Payments', 'Average_Medicare_Payments']
    #     return pd.read_csv(os.path.join(self._datafile_dir, "IPPS_Provider_Data.csv"),
    #                        header=0,
    #                        names=headers,
    #                        converters={'Average_Covered_Charges': lambda x: float(x.replace('$', '')),
    #                                    'Average_Total_Payments': lambda x: float(x.replace('$', '')),
    #                                    'Average_Medicare_Payments': lambda x: float(x.replace('$', ''))})

    def get_mdc_code_data(self):
        """
        This method pulls the mdc to drg mapping table from a csv file
        
        return: matrix of drg codes and associated mdc
        """
        headers = ['MDC', 'Description', 'MS-DRG', 'MS-DRG(low)', 'MS-DRG(high)', 'alt']
        mdc = pd.read_csv(os.path.join(self._datafile_dir, "DRGtoMDC.csv"),
                          header=0,
                          names=headers)
        """the MDCs map close to the index (mdc starts at 0; index starts at 0)"""

        """create a drg to mdc mapping"""
        drg_low = mdc['MS-DRG(low)']
        drg_high = mdc['MS-DRG(high)']
        mdc_codes = mdc['MDC']
        # build the table
        mdc_codes = mdc_codes.to_frame()
        mdc_codes = mdc_codes.merge(drg_low.to_frame(), left_index=True, right_index=True)
        mdc_codes = mdc_codes.merge(drg_high.to_frame(), left_index=True, right_index=True)

        return mdc_codes

    # def map_ipps_drg_codes_to_mdc(self, ipps_data):
    #     """
    #     maps ipps drg codes to the corresponding mdc value
    #     returns: mdc_codes
    #     """
    #     mdc_codes = self.get_mdc_code_data()
    #     # build a series of the MDCs.  Then we can merge
    #     ipps_idx = ipps_data.index.values
    #     mdc_df = pd.DataFrame(columns=['MDC'], index=ipps_idx)
    #     # mdc_df id the dataframe of mdc values we will merge later
    #
    #     for i, row in ipps_data.iterrows():
    #         #StrVal, rest = row['DRG Definition'].split('-', 1)
    #         #DRG_code = int(StrVal)
    #         DRG_code = row["DRG_Code"]
    #         """
    #         now to convert the DRG code to MDC.
    #         Easy answer: a 25-case structure; but this is not what we want
    #         Best answer: use a range check (while loop to iterate through low values)
    #         Today's answer: a for loop with conditional and a break statement
    #
    #         """
    #         mdc_value = '1'  # first MDC Code in the table
    #         mdc_df.set_value(i, 'MDC', mdc_value)
    #         for j, row2 in mdc_codes.iterrows():
    #             if DRG_code > int(row2['MS-DRG(high)']):
    #                 break
    #             else:
    #                 mdc_value = row2['MDC']
    #                 mdc_df.set_value(i, 'MDC', mdc_value)
    #
    #     ipps_data = ipps_data.merge(mdc_df, left_index=True, right_index=True)
    #
    #     return ipps_data

    def add_mdc_codes_to_ipps(self, ipps_data):
        mdc_codes = self.get_mdc_code_data()
        ipps_data["MDC"] = [[code[0] for code in mdc_codes.values if drg_code >= code[1] and drg_code <= code[2]][0] for drg_code in ipps_data.DRG_Code.values]
