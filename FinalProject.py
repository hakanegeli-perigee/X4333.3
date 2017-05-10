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

    # ipps data now has region, urban and MDC fields added
    ipps_data.to_csv("IPPS_Provider_Data_Merged.csv")
    print("done")


if __name__ == "__main__":
    main()
