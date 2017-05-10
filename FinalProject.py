import pandas as pd
from ipps import IppsData
from DRGtoMDC import DRGtoMDC

def main():
    """
    Entry point for main logic
    
    """
    # IppsData object know how to read the input data and add the necessary fields we need
    ipps = IppsData()

    # load data initializes the object
    ipps.load()

    # .data property returns a pandas DataFrame
    ipps_data = ipps.data

    drg_mdc = DRGtoMDC()
    drg_mdc.add_mdc_codes_to_ipps(ipps_data)

    # this is how you can save the ipps data to a file if want to look at it in Excel
    #ipps_data.to_csv("IPPS_Provider_Data_Merged.csv")

    # this is how to select the columns you want from the DataFrame
    mdc_codes_and_regions = ipps_data[["MDC", "Region", "Average_Total_Payments"]]
    print(type(mdc_codes_and_regions))
    print("Number of MDC Code and Regions:\n{}\n".format(len(mdc_codes_and_regions)))

    # this is how to group the values and perform an aggregate function
    mdc_codes_and_regions_summary = mdc_codes_and_regions.groupby(["MDC", "Region"])["Average_Total_Payments"].sum()
    print("Group by MDC Code and Regions:\n{}\n".format(mdc_codes_and_regions_summary.head(8)))

    # this is how to perform a search within the data
    mdc_codes_and_regions_search = mdc_codes_and_regions[(mdc_codes_and_regions["MDC"] == 23) & (mdc_codes_and_regions["Region"] == "WEST") & (mdc_codes_and_regions["Average_Total_Payments"] > 8000)]
    print("Search Results:\n{}\n".format(mdc_codes_and_regions_search))

    # this is how to get unique values for a specific column
    print("Unique Regions (inc NaN):\n{}\n".format(mdc_codes_and_regions.Region.unique()))

    # this is how to get unique not null values for a specific column
    print("Unique Regions V1:\n{}\n".format(mdc_codes_and_regions.Region[pd.isnull(mdc_codes_and_regions.Region) == False].unique()))
    # or
    print("Unique Regions V2:\n{}\n".format(mdc_codes_and_regions.Region[mdc_codes_and_regions.Region.notnull()].unique()))

    # this is how you can set a value to columns with Null/NaN. It does not modify the source data!!!
    print("Unique Regions (nan is set to UNK):\n{}\n".format(mdc_codes_and_regions.Region.fillna("UNK").unique()))

    print("done")


if __name__ == "__main__":
    main()
