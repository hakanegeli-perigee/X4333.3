from ipps import IppsData


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

    # since it's a dataframe all dataframe methods and properties can be used on the .data
    # ex. get the column names
    print(ipps_data.columns)

    # ex2. get the columns you are interested using a list
    print(ipps_data[["DRG_Definition", "Provider_Name"]].head(10))

    # this is temporary, just to visualize the merged data set
    ipps_data.to_csv("IPPS_Provider_Data_Merged.csv")


if __name__ == "__main__":
    main()
