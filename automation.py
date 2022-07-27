import pandas as pd
import os
import logging
import datetime

#Logging Module
logger = logging.getLogger()
logfilename = "automation-{datetime}.log".format(datetime=datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
filehandler = logging.FileHandler(str(logfilename))
LOG_FORMAT = filehandler.setFormatter(logging.Formatter('%(asctime)s  %(filename)s  %(levelname)s: %(message)s'))
handlers = logger.addHandler(filehandler)
LOG_LEVEL = logger.setLevel(logging.INFO)
logging.basicConfig(filename=logfilename, level=LOG_LEVEL, handlers=handlers, format=LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

def remove_file(FileName):
    """
    Remove a file from a given path
    :param FileName: the path to the file to be removed
    """
    if not os.path.isfile(FileName):
        logger.info("This file does not exist {}".format(FileName))
        return
    logger.info("Try to remove {}".format(FileName))
    try:
        os.remove(FileName)
        logger.info("Removed {}".format(FileName))
    except FileNotFoundError:
        pass

def get_prodcut_deatils(product_id):
    """
    Fetch the cost of the product based on ID
    :param product_id: ID of the product
    """
    ProductData = pd.read_csv("products.csv")
    SearchData = ProductData[ProductData["id"] == product_id]
    ReturnData = SearchData["cost"]
    return (ReturnData.values[0])

def get_customer_deatils(col_name,customer_id):
    """
    Fetch the details (firstname/lastname) of the customer based on ID
    :param cusotmer_id: ID of the customer
    """
    CustomerData = pd.read_csv("customers.csv")
    SearchData = CustomerData[CustomerData["id"] == customer_id]
    ReturnData = SearchData[col_name]
    return (ReturnData.values[0])

def generate_order_price(OutputFileName):
    """
    Generate the order_prices.csv file based on requirement
    :param OutputFileName: Name of the output file name
    """
    #Remove the file from path if exists
    remove_file(OutputFileName)
    #Read the Order file to generate the outputfile
    OrderData = pd.read_csv("orders.csv")
    for index, row in OrderData.iterrows():
        ProductId = row['products'].replace(' ', '')
        OrderTotal = 0
        #Reading data ProdcutId column value for calculation
        for readdata in ProductId:
            OrderTotal = OrderTotal+get_prodcut_deatils(int(readdata))
        #Creating the dataframe for writing into csv file
        OrderPrice = pd.DataFrame({'id': [row.id],'euros': [OrderTotal]})
        OrderPrice.to_csv(OutputFileName, mode='a', index=False, header=not os.path.exists(OutputFileName))
    logger.info("Successfully created the file  {}".format(OutputFileName))

def generate_product_customers(OutputFileName):
    """
    Generate the product_customers.csv file based on requirement
    :param OutputFileName: Name of the output file name
    """
    #Remove the file from path if exists
    remove_file(OutputFileName)
    ProductData = pd.read_csv("products.csv")
    for index, row in ProductData.iterrows():
        ProdId=row['id']
        #Read the Order file to generate the outputfile
        OrderData = pd.read_csv("orders.csv")
        sorted_df = OrderData.sort_values(by='customer', ascending=True)
        CustList = []
        for index, row in sorted_df.iterrows():
            ProductId = row['products'].replace(' ', '')
            CustomerId = row['customer']
            #Reading data ProdcutId column value for calculation
            for readdata in ProductId:
                if int(readdata) == ProdId:
                    data = CustList.append(CustomerId) if CustomerId not in CustList else CustList

        #Sorting the data based on Customer ID
        SortedCustomerId = sorted(CustList)
        ProductCustomer = pd.DataFrame({'id':ProdId, 'customer_ids':[SortedCustomerId]})
        ProductCustomer.to_csv(OutputFileName, mode='a', index=False, header=not os.path.exists(OutputFileName))

    #Replace the Comma with space and remove the extra bracket
    ReplaceProductData = pd.read_csv(OutputFileName)
    ReplaceProductData['customer_ids'] = ReplaceProductData['customer_ids'].str.replace(',', '').str.replace('[', '').str.replace(']', '')
    ReplaceProductData.to_csv(OutputFileName, index=False)
    logger.info("Successfully created the file  {}".format(OutputFileName))

def generate_customer_ranking(OutputFileName):
    """
    Generate the customer_ranking.csv file based on requirement
    :param OutputFileName: Name of the output file name
    """
    #Remove the file from path if exists
    remove_file(OutputFileName)
    #Read the Order file to generate the outputfile
    OrderData = pd.read_csv("orders.csv")
    SortedOrderData = OrderData.sort_values(by='customer', ascending=True)
    OrderTotal = 0
    PrevCustId = 0.1
    for index, row in SortedOrderData.iterrows():
        ProductId = row['products'].replace(' ', '')
        #Reading data ProdcutId column value for calculation
        if PrevCustId < row.customer:
            OrderTotal = 0
        for readdata in ProductId:
            OrderTotal = OrderTotal+get_prodcut_deatils(int(readdata))

        if PrevCustId != row['customer']:
            # Creating the dataframe for writing into csv file
            CustomerRanking = pd.DataFrame({'customer': [row.customer], 'firstname': get_customer_deatils('firstname',row.customer),'lastname': get_customer_deatils('lastname',row.customer),'euros': [OrderTotal]})
            CustomerRanking.to_csv(OutputFileName, mode='a', index=False, header=not os.path.exists(OutputFileName))
            OrderTotal=0
        else:
            OrderTotal = OrderTotal+OrderTotal
            #Update the Euros values if its exists in CSV file
            UpdatedCustomerData = pd.read_csv(OutputFileName)
            UpdatedCustomerData.loc[UpdatedCustomerData['customer'] == row.customer, 'euros'] = [OrderTotal]
            UpdatedCustomerData.to_csv(OutputFileName,index=False)

        PrevCustId = row['customer']

        #Sorting and rewrite the data based on Euros values (Decending)
        SortedCustomerData = pd.read_csv(OutputFileName)
        SortedCustomerData.sort_values(by=['euros'], inplace=True,ascending=False)
        SortedCustomerData.to_csv(OutputFileName,index=False)
    logger.info("Successfully created the file  {}".format(OutputFileName))

def main():
    logger.info("Start File Process")
    generate_order_price(OutputFileName='order_prices.csv')
    generate_product_customers(OutputFileName='product_customers.csv')
    generate_customer_ranking(OutputFileName='customer_ranking.csv')
    logger.info("End File Process")

if __name__ == "__main__":
    main()
