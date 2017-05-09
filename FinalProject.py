from ipps import IppsData


def main():
    """
    Entry point for main logic
    
    :return: None
    """
    
    # IppsData object know how to read the input data and add the necessary fields we need
    ipps = IppsData()

    # get_data() method returns a pandas DataFrame
    ipps_data = ipps.get_data()

    # this is temporary, just to visualize the merged data set
    ipps_data.to_csv("IPPS_Provider_Data_Merged.csv")


if __name__ == "__main__":
    main()
