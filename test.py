from intuitlib.client import AuthClient
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects import Invoice
from quickbooks.objects import CompanyInfo
from quickbooks.objects import Payment
from quickbooks.objects import Estimate
from quickbooks.objects import Bill
from quickbooks.objects import Vendor
from quickbooks.objects import Item
from intuitlib.enums import Scopes
from flask import render_template, Flask, request
import requests, json

"""
auth_client = AuthClient(
        client_id='ABwZokNxeDSMNmhnW8TxITwUP6MCEalhNra0dUBp9HaA2zhhLH',
        client_secret='zMuR80GLsPU5EkwqV4MILOzv5exHPPJZoiUNasMx',
        environment='sandbox',
        redirect_uri='http://localhost:5000/callback',
)
"""

auth_client = AuthClient(
        client_id='ABbKs5w2syrVw4vN39nf42uD8crY4lUJRnDFwcXjly9pgWUKBx',
        client_secret='YnSlXPNXC6iXUg9HR8DrWD5T9K6gGgFxYmDjy8GF',
        environment='sandbox',
        redirect_uri='http://localhost:5000/callback',
)


scopes = [
    Scopes.ACCOUNTING,
]
auth_url = auth_client.get_authorization_url(scopes)



#customers = Customer.all(qb=client)AB11589204914pldGqmkeN9QDxS5mTu4vyA7l5TblrLiqMLSBG
#customers = Customer.all(order_by='FamilyName, GivenName', qb=client)
#invoices = Invoice.filter(order_by='TotalAmt', qb=client)
#company = CompanyInfo.all(qb=client)
#payment = Payment.all(qb=client)
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('test.html', url=auth_url)


@app.route('/callback')
def callback():

    code = request.args.get('code', None)
    realm = request.args.get('realmId', None)
    auth_client.get_bearer_token(code,realm_id=realm)
    base_url = "https://sandbox-quickbooks.api.intuit.com"
    url = '{0}/v3/company/{1}/companyinfo/{1}'.format(base_url, auth_client.realm_id)
    auth_header = 'Bearer {0}'.format(auth_client.access_token)
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)
    print(response.json())

    #extraction des données Bill
    url='{0}/v3/company/{1}/query?query=select * from bill maxresults 1&minorversion=45'.format(base_url,auth_client.realm_id)
    get_bill=requests.get(url,headers=headers)
    data_bill=get_bill.json()
    print(data_bill)
    #stockage des information Bill dans BD
    bill = data_bill['QueryResponse']['Bill']
    for i in range(0,len(bill)):
        due_date=bill[i]['DueDate']
        balance=bill[i]['Balance']
        id=bill[i]['Id']
        currency=bill[i]['CurrencyRef']['value']
        taxpercent=bill[i]['TxnTaxDetail']['TaxLine'][0]['TaxLineDetail']['TaxPercent']
        transactionLocationType=bill[i]['TransactionLocationType']
        totalAmt=bill[i]['TotalAmt']
        globalTaxCalculation=bill[i]['GlobalTaxCalculation']
        print(taxpercent)

    #extraction des données Invoice
    url='{0}/v3/company/{1}/query?query=select * from Invoice &minorversion=45'.format(base_url,auth_client.realm_id)
    get_all_invoices = requests.get(url, headers=headers)
    data_invoices = get_all_invoices.json()
    print(data_invoices)
    print(data_invoices['QueryResponse']['Invoice'])

    #stockage des informations Invoice dans BD
    invoice=data_invoices['QueryResponse']['Invoice']
    for i in range(0,len(invoice)):
        due_date = invoice[i]['DueDate']
        balance = invoice[i]['Balance']
        id = invoice[i]['Id']
        transactionLocationType = invoice[i]['TransactionLocationType']
        totalAmt = invoice[i]['TotalAmt']
        globalTaxCalculation = invoice[i]['GlobalTaxCalculation']

    #extraction des données Customer
    url = '{0}/v3/company/{1}/query?query=select * from Customer &minorversion=45'.format(base_url, auth_client.realm_id)
    get_all_customers = requests.get(url, headers=headers)
    data_customers = get_all_customers.json()
    print(data_customers)


    return render_template('callback.html')


@app.route('/getCall')
def getCall():
    client = QuickBooks(
        auth_client=auth_client,
        refresh_token=auth_client.refresh_token,
        company_id=auth_client.realm_id,
    )
    print(client.refresh_token)
    company = CompanyInfo.all(qb=client)
    payment = Payment.all(qb=client)
    invoices = Invoice.filter(order_by='TotalAmt', qb=client)
    estimate = Estimate.all(qb=client)
    bill = Bill.all(qb=client)
    vendor = Vendor.all(qb=client)
    item = Item.all(qb=client)
    print(company)
    for comp in company:
        print(comp.CompanyName)
    for pay in payment:
        print(pay.TotalAmt)
    for inv in invoices:
        print(inv.TotalAmt)
    for bi in bill:
        print(bi.DueDate)
    for ven in vendor:
        print(ven.DisplayName)
    for it in item:
        print(it.Name)
    for est in estimate:
        print(est.BillEmail)
    return render_template('getCall.html')


def main():
    #print(auth_client.get_bearer_token('AB11580487415Litl227c5Dr3rZiRwDwjz1XgA35UzZtcjUlZt', realm_id='4620816365004686200'))
    print(auth_client.refresh_token)
    print(auth_url)


if __name__ == '__main__':
    app.run()

resp={'QueryResponse': {'Invoice': [{'AllowIPNPayment': False, 'AllowOnlinePayment': False, 'AllowOnlineCreditCardPayment': False, 'AllowOnlineACHPayment': False, 'domain': 'QBO', 'sparse': False, 'Id': '33', 'SyncToken': '1', 'MetaData': {'CreateTime': '2020-02-29T02:34:17-08:00', 'LastUpdatedTime': '2020-02-29T02:36:01-08:00'}, 'CustomField': [], 'DocNumber': '1013', 'TxnDate': '2020-02-29', 'DepartmentRef': {'value': '1', 'name': 'Paris 6e'}, 'CurrencyRef': {'value': 'EUR', 'name': 'Euro'}, 'LinkedTxn': [], 'Line': [{'Id': '1', 'LineNum': 1, 'Amount': 135.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '4', 'name': 'Caisse de 6 bouteilles de vin'}, 'UnitPrice': 135, 'Qty': 1, 'ItemAccountRef': {'value': '1', 'name': '70710000 Ventes de Marchandises (ou groupe) A 20%'}, 'TaxCodeRef': {'value': '31'}}}, {'Id': '2', 'LineNum': 2, 'Amount': 2.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '10', 'name': 'Pain tradition'}, 'UnitPrice': 2, 'Qty': 1, 'ItemAccountRef': {'value': '112', 'name': '70710001 Marchandises (ou groupe) A France 5,5%'}, 'TaxCodeRef': {'value': '28'}}}, {'Amount': 137.0, 'DetailType': 'SubTotalLineDetail', 'SubTotalLineDetail': {}}, {'Amount': 0, 'DetailType': 'DiscountLineDetail', 'DiscountLineDetail': {'PercentBased': False}}], 'TxnTaxDetail': {'TotalTax': 27.11, 'TaxLine': [{'Amount': 27.0, 'DetailType': 'TaxLineDetail', 'TaxLineDetail': {'TaxRateRef': {'value': '24'}, 'PercentBased': True, 'TaxPercent': 20, 'NetAmountTaxable': 135.0}}, {'Amount': 0.11, 'DetailType': 'TaxLineDetail', 'TaxLineDetail': {'TaxRateRef': {'value': '22'}, 'PercentBased': True, 'TaxPercent': 5.5, 'NetAmountTaxable': 2.0}}]}, 'TransactionLocationType': 'WithinFrance', 'CustomerRef': {'value': '14', 'name': 'Auchan hypermarché'}, 'BillAddr': {'Id': '13', 'Line1': '1 Rue Abel Rabaud', 'City': 'Paris', 'PostalCode': '75011', 'Lat': '48.8693793', 'Long': '2.3716308'}, 'FreeFormAddress': False, 'ClassRef': {'value': '301200000000000002081', 'name': 'Entreprises'}, 'SalesTermRef': {'value': '3'}, 'DueDate': '2020-02-29', 'GlobalTaxCalculation': 'TaxExcluded', 'TotalAmt': 164.11, 'PrintStatus': 'NotSet', 'EmailStatus': 'NotSet', 'BillEmail': {'Address': 'julien_fournier@intuit.com'}, 'Balance': 164.11, 'DiscountAmt': 0}, {'AllowIPNPayment': False, 'AllowOnlinePayment': False, 'AllowOnlineCreditCardPayment': False, 'AllowOnlineACHPayment': False, 'EInvoiceStatus': 'Sent', 'domain': 'QBO', 'sparse': False, 'Id': '32', 'SyncToken': '1', 'MetaData': {'CreateTime': '2020-02-29T00:26:38-08:00', 'LastUpdatedTime': '2020-02-29T00:27:12-08:00'}, 'CustomField': [], 'DocNumber': '1012', 'TxnDate': '2020-03-01', 'DepartmentRef': {'value': '1', 'name': 'Paris 6e'}, 'CurrencyRef': {'value': 'EUR', 'name': 'Euro'}, 'LinkedTxn': [], 'Line': [{'Id': '1', 'LineNum': 1, 'Description': 'Atelier gâteau: 3 heures', 'Amount': 95.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '14', 'name': 'Atelier gâteau'}, 'UnitPrice': 95, 'Qty': 1, 'ItemAccountRef': {'value': '3', 'name': '70610000 Prestations de services 20%'}, 'TaxCodeRef': {'value': '31'}}}, {'Amount': 95.0, 'DetailType': 'SubTotalLineDetail', 'SubTotalLineDetail': {}}, {'Amount': 0, 'DetailType': 'DiscountLineDetail', 'DiscountLineDetail': {'PercentBased': False}}], 'TxnTaxDetail': {'TotalTax': 19.0, 'TaxLine': [{'Amount': 19.0, 'DetailType': 'TaxLineDetail', 'TaxLineDetail': {'TaxRateRef': {'value': '24'}, 'PercentBased': True, 'TaxPercent': 20, 'NetAmountTaxable': 95.0}}]}, 'TransactionLocationType': 'WithinFrance', 'CustomerRef': {'value': '14', 'name': 'Auchan hypermarché'}, 'BillAddr': {'Id': '13', 'Line1': '1 Rue Abel Rabaud', 'City': 'Paris', 'PostalCode': '75011', 'Lat': '48.8693793', 'Long': '2.3716308'}, 'FreeFormAddress': False, 'SalesTermRef': {'value': '3'}, 'DueDate': '2020-03-31', 'GlobalTaxCalculation': 'TaxExcluded', 'TotalAmt': 114.0, 'PrintStatus': 'NeedToPrint', 'EmailStatus': 'EmailSent', 'BillEmail': {'Address': 'julien_fournier@intuit.com'}, 'Balance': 114.0, 'DeliveryInfo': {'DeliveryType': 'Email', 'DeliveryTime': '2020-02-29T00:26:46-08:00'}, 'DiscountAmt': 0}, {'AllowIPNPayment': False, 'AllowOnlinePayment': False, 'AllowOnlineCreditCardPayment': False, 'AllowOnlineACHPayment': False, 'EInvoiceStatus': 'Sent', 'domain': 'QBO', 'sparse': False, 'Id': '31', 'SyncToken': '1', 'MetaData': {'CreateTime': '2020-02-28T00:29:23-08:00', 'LastUpdatedTime': '2020-02-28T00:29:30-08:00'}, 'CustomField': [], 'DocNumber': '1011', 'TxnDate': '2020-02-29', 'DepartmentRef': {'value': '1', 'name': 'Paris 6e'}, 'CurrencyRef': {'value': 'EUR', 'name': 'Euro'}, 'LinkedTxn': [], 'Line': [{'Id': '1', 'LineNum': 1, 'Description': 'Atelier gâteau: 3 heures', 'Amount': 95.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '14', 'name': 'Atelier gâteau'}, 'UnitPrice': 95, 'Qty': 1, 'ItemAccountRef': {'value': '3', 'name': '70610000 Prestations de services 20%'}, 'TaxCodeRef': {'value': '31'}}}, {'Amount': 95.0, 'DetailType': 'SubTotalLineDetail', 'SubTotalLineDetail': {}}, {'Amount': 0, 'DetailType': 'DiscountLineDetail', 'DiscountLineDetail': {'PercentBased': False}}], 'TxnTaxDetail': {'TotalTax': 19.0, 'TaxLine': [{'Amount': 19.0, 'DetailType': 'TaxLineDetail', 'TaxLineDetail': {'TaxRateRef': {'value': '24'}, 'PercentBased': True, 'TaxPercent': 20, 'NetAmountTaxable': 95.0}}]}, 'TransactionLocationType': 'WithinFrance', 'CustomerRef': {'value': '14', 'name': 'Auchan hypermarché'}, 'BillAddr': {'Id': '13', 'Line1': '1 Rue Abel Rabaud', 'City': 'Paris', 'PostalCode': '75011', 'Lat': '48.8693793', 'Long': '2.3716308'}, 'FreeFormAddress': False, 'SalesTermRef': {'value': '3'}, 'DueDate': '2020-03-30', 'GlobalTaxCalculation': 'TaxExcluded', 'TotalAmt': 114.0, 'PrintStatus': 'NeedToPrint', 'EmailStatus': 'EmailSent', 'BillEmail': {'Address': 'julien_fournier@intuit.com'}, 'Balance': 114.0, 'DeliveryInfo': {'DeliveryType': 'Email', 'DeliveryTime': '2020-02-28T00:29:24-08:00'}, 'DiscountAmt': 0}, {'AllowIPNPayment': False, 'AllowOnlinePayment': False, 'AllowOnlineCreditCardPayment': False, 'AllowOnlineACHPayment': False, 'EInvoiceStatus': 'Sent', 'domain': 'QBO', 'sparse': False, 'Id': '30', 'SyncToken': '1', 'MetaData': {'CreateTime': '2020-02-28T00:28:45-08:00', 'LastUpdatedTime': '2020-02-28T00:29:23-08:00'}, 'CustomField': [], 'DocNumber': '1010', 'TxnDate': '2020-02-28', 'DepartmentRef': {'value': '1', 'name': 'Paris 6e'}, 'CurrencyRef': {'value': 'EUR', 'name': 'Euro'}, 'LinkedTxn': [], 'Line': [{'Id': '1', 'LineNum': 1, 'Description': 'Atelier gâteau: 3 heures', 'Amount': 95.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '14', 'name': 'Atelier gâteau'}, 'UnitPrice': 95, 'Qty': 1, 'ItemAccountRef': {'value': '3', 'name': '70610000 Prestations de services 20%'}, 'TaxCodeRef': {'value': '31'}}}, {'Amount': 95.0, 'DetailType': 'SubTotalLineDetail', 'SubTotalLineDetail': {}}, {'Amount': 0, 'DetailType': 'DiscountLineDetail', 'DiscountLineDetail': {'PercentBased': False}}], 'TxnTaxDetail': {'TotalTax': 19.0, 'TaxLine': [{'Amount': 19.0, 'DetailType': 'TaxLineDetail', 'TaxLineDetail': {'TaxRateRef': {'value': '24'}, 'PercentBased': True, 'TaxPercent': 20, 'NetAmountTaxable': 95.0}}]}, 'TransactionLocationType': 'WithinFrance', 'CustomerRef': {'value': '14', 'name': 'Auchan hypermarché'}, 'BillAddr': {'Id': '13', 'Line1': '1 Rue Abel Rabaud', 'City': 'Paris', 'PostalCode': '75011', 'Lat': '48.8693793', 'Long': '2.3716308'}, 'FreeFormAddress': False, 'SalesTermRef': {'value': '3'}, 'DueDate': '2020-03-29', 'GlobalTaxCalculation': 'TaxExcluded', 'TotalAmt': 114.0, 'PrintStatus': 'NeedToPrint', 'EmailStatus': 'EmailSent', 'BillEmail': {'Address': 'julien_fournier@intuit.com'}, 'Balance': 114.0, 'DeliveryInfo': {'DeliveryType': 'Email', 'DeliveryTime': '2020-02-28T00:28:52-08:00'}, 'DiscountAmt': 0}, {'AllowIPNPayment': False, 'AllowOnlinePayment': False, 'AllowOnlineCreditCardPayment': False, 'AllowOnlineACHPayment': False, 'domain': 'QBO', 'sparse': False, 'Id': '29', 'SyncToken': '1', 'MetaData': {'CreateTime': '2020-02-27T05:50:43-08:00', 'LastUpdatedTime': '2020-02-27T05:50:52-08:00'}, 'CustomField': [], 'DocNumber': '1009', 'TxnDate': '2020-02-27', 'DepartmentRef': {'value': '1', 'name': 'Paris 6e'}, 'CurrencyRef': {'value': 'EUR', 'name': 'Euro'}, 'LinkedTxn': [{'TxnId': '28', 'TxnType': 'Estimate'}], 'Line': [{'Id': '1', 'LineNum': 1, 'Amount': 135.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '4', 'name': 'Caisse de 6 bouteilles de vin'}, 'UnitPrice': 135, 'Qty': 1, 'ItemAccountRef': {'value': '1', 'name': '70710000 Ventes de Marchandises (ou groupe) A 20%'}, 'TaxCodeRef': {'value': '31'}}}, {'Amount': 135.0, 'DetailType': 'SubTotalLineDetail', 'SubTotalLineDetail': {}}, {'Amount': 0, 'DetailType': 'DiscountLineDetail', 'DiscountLineDetail': {'PercentBased': False}}], 'TxnTaxDetail': {'TotalTax': 27.0, 'TaxLine': [{'Amount': 27.0, 'DetailType': 'TaxLineDetail', 'TaxLineDetail': {'TaxRateRef': {'value': '24'}, 'PercentBased': True, 'TaxPercent': 20, 'NetAmountTaxable': 135.0}}]}, 'TransactionLocationType': 'WithinFrance', 'CustomerRef': {'value': '5', 'name': 'Caroline Corbeil'}, 'BillAddr': {'Id': '6', 'Line1': '56 Mont Blanc', 'City': 'Paris', 'Country': 'France', 'PostalCode': '75005', 'Lat': '48.84958880000001', 'Long': '2.2737159'}, 'FreeFormAddress': False, 'SalesTermRef': {'value': '3'}, 'DueDate': '2020-03-28', 'GlobalTaxCalculation': 'TaxExcluded', 'TotalAmt': 162.0, 'PrintStatus': 'NotSet', 'EmailStatus': 'NotSet', 'BillEmail': {'Address': 'ccorbeil@exemple.fr'}, 'Balance': 162.0, 'DiscountAmt': 0}, {'AllowIPNPayment': False, 'AllowOnlinePayment': False, 'AllowOnlineCreditCardPayment': False, 'AllowOnlineACHPayment': False, 'EInvoiceStatus': 'Viewed', 'ECloudStatusTimeStamp': '2020-02-22T02:21:37-08:00', 'domain': 'QBO', 'sparse': False, 'Id': '25', 'SyncToken': '4', 'MetaData': {'CreateTime': '2020-02-20T06:16:01-08:00', 'LastUpdatedTime': '2020-02-22T02:21:37-08:00'}, 'CustomField': [], 'DocNumber': '1008', 'TxnDate': '2020-02-20', 'DepartmentRef': {'value': '1', 'name': 'Paris 6e'}, 'CurrencyRef': {'value': 'EUR', 'name': 'Euro'}, 'LinkedTxn': [], 'Line': [{'Id': '1', 'LineNum': 1, 'Amount': 20.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '7', 'name': 'Gateaux'}, 'UnitPrice': 20, 'Qty': 1, 'ItemAccountRef': {'value': '113', 'name': '70710002 Marchandises (ou groupe) A France 10%'}, 'TaxCodeRef': {'value': '26'}}}, {'Id': '2', 'LineNum': 2, 'Amount': 4.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '11', 'name': 'Paris Brest'}, 'UnitPrice': 4, 'Qty': 1, 'ItemAccountRef': {'value': '113', 'name': '70710002 Marchandises (ou groupe) A France 10%'}, 'TaxCodeRef': {'value': '26'}}}, {'Amount': 24.0, 'DetailType': 'SubTotalLineDetail', 'SubTotalLineDetail': {}}, {'Amount': 0, 'DetailType': 'DiscountLineDetail', 'DiscountLineDetail': {'PercentBased': False}}], 'TxnTaxDetail': {'TotalTax': 2.4, 'TaxLine': [{'Amount': 2.4, 'DetailType': 'TaxLineDetail', 'TaxLineDetail': {'TaxRateRef': {'value': '19'}, 'PercentBased': True, 'TaxPercent': 10, 'NetAmountTaxable': 24.0}}]}, 'TransactionLocationType': 'WithinFrance', 'CustomerRef': {'value': '6', 'name': 'Christiane Hile'}, 'BillAddr': {'Id': '7', 'Line1': '68  Grande Allée', 'City': 'Paris', 'Country': 'France', 'PostalCode': '75006', 'Lat': '48.8773177', 'Long': '2.2855365'}, 'FreeFormAddress': False, 'SalesTermRef': {'value': '3'}, 'DueDate': '2020-03-21', 'GlobalTaxCalculation': 'TaxExcluded', 'TotalAmt': 26.4, 'PrintStatus': 'NotSet', 'EmailStatus': 'EmailSent', 'BillEmail': {'Address': 'julien_fournier@intuit.com'}, 'Balance': 26.4, 'DeliveryInfo': {'DeliveryType': 'Email', 'DeliveryTime': '2020-02-22T02:15:28-08:00'}, 'DiscountAmt': 0}, {'AllowIPNPayment': False, 'AllowOnlinePayment': False, 'AllowOnlineCreditCardPayment': False, 'AllowOnlineACHPayment': False, 'domain': 'QBO', 'sparse': False, 'Id': '1', 'SyncToken': '4', 'MetaData': {'CreateTime': '2020-02-19T07:12:03-08:00', 'LastUpdatedTime': '2020-02-19T07:46:06-08:00'}, 'CustomField': [], 'DocNumber': '1001', 'TxnDate': '2020-01-11', 'DepartmentRef': {'value': '1', 'name': 'Paris 6e'}, 'CurrencyRef': {'value': 'EUR', 'name': 'Euro'}, 'LinkedTxn': [{'TxnId': '5', 'TxnType': 'Payment'}], 'Line': [{'Id': '1', 'LineNum': 1, 'Description': 'Paris Brest', 'Amount': 4000.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '11', 'name': 'Paris Brest'}, 'UnitPrice': 4, 'Qty': 1000, 'ItemAccountRef': {'value': '1', 'name': '70710000 Ventes de Marchandises (ou groupe) A 20%'}, 'TaxCodeRef': {'value': '31'}}}, {'Amount': 4000.0, 'DetailType': 'SubTotalLineDetail', 'SubTotalLineDetail': {}}, {'Amount': 0, 'DetailType': 'DiscountLineDetail', 'DiscountLineDetail': {'PercentBased': False}}], 'TxnTaxDetail': {'TotalTax': 800.0, 'TaxLine': [{'Amount': 800.0, 'DetailType': 'TaxLineDetail', 'TaxLineDetail': {'TaxRateRef': {'value': '24'}, 'PercentBased': True, 'TaxPercent': 20, 'NetAmountTaxable': 4000.0}}]}, 'TransactionLocationType': 'WithinFrance', 'CustomerRef': {'value': '14', 'name': 'Auchan hypermarché'}, 'CustomerMemo': {'value': 'Merci de votre confiance'}, 'BillAddr': {'Id': '13', 'Line1': '1 Rue Abel Rabaud', 'City': 'Paris', 'PostalCode': '75011', 'Lat': '48.8693793', 'Long': '2.3716308'}, 'FreeFormAddress': False, 'ClassRef': {'value': '301200000000000002082', 'name': 'Magasins'}, 'SalesTermRef': {'value': '3'}, 'DueDate': '2020-02-10', 'GlobalTaxCalculation': 'TaxExcluded', 'TotalAmt': 4800.0, 'PrintStatus': 'NotSet', 'EmailStatus': 'NotSet', 'Balance': 3800.0, 'DiscountAmt': 0}, {'AllowIPNPayment': False, 'AllowOnlinePayment': False, 'AllowOnlineCreditCardPayment': False, 'AllowOnlineACHPayment': False, 'domain': 'QBO', 'sparse': False, 'Id': '4', 'SyncToken': '1', 'MetaData': {'CreateTime': '2020-02-19T07:16:22-08:00', 'LastUpdatedTime': '2020-02-19T07:45:48-08:00'}, 'CustomField': [], 'DocNumber': '1004', 'TxnDate': '2020-02-09', 'DepartmentRef': {'value': '1', 'name': 'Paris 6e'}, 'CurrencyRef': {'value': 'EUR', 'name': 'Euro'}, 'LinkedTxn': [], 'Line': [{'Id': '1', 'LineNum': 1, 'Description': 'Atelier gâteau: 3 heures', 'Amount': 950.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountRate': 5, 'DiscountAmt': 47.5, 'ItemRef': {'value': '14', 'name': 'Atelier gâteau'}, 'UnitPrice': 95, 'Qty': 10, 'ItemAccountRef': {'value': '3', 'name': '70610000 Prestations de services 20%'}, 'TaxCodeRef': {'value': '31'}}}, {'Amount': 950.0, 'DetailType': 'SubTotalLineDetail', 'SubTotalLineDetail': {}}, {'Amount': 47.5, 'DetailType': 'DiscountLineDetail', 'DiscountLineDetail': {'PercentBased': False}}], 'TxnTaxDetail': {'TotalTax': 180.5, 'TaxLine': [{'Amount': 180.5, 'DetailType': 'TaxLineDetail', 'TaxLineDetail': {'TaxRateRef': {'value': '24'}, 'PercentBased': True, 'TaxPercent': 20, 'NetAmountTaxable': 902.5}}]}, 'TransactionLocationType': 'WithinFrance', 'CustomerRef': {'value': '5', 'name': 'Caroline Corbeil'}, 'BillAddr': {'Id': '6', 'Line1': '56 Mont Blanc', 'City': 'Paris', 'Country': 'France', 'PostalCode': '75005', 'Lat': '48.84958880000001', 'Long': '2.2737159'}, 'FreeFormAddress': False, 'ClassRef': {'value': '301200000000000002081', 'name': 'Entreprises'}, 'SalesTermRef': {'value': '3'}, 'DueDate': '2020-03-10', 'GlobalTaxCalculation': 'TaxExcluded', 'TotalAmt': 1083.0, 'PrintStatus': 'NotSet', 'EmailStatus': 'NotSet', 'BillEmail': {'Address': 'ccorbeil@exemple.fr'}, 'Balance': 1083.0, 'DiscountAmt': 0}, {'AllowIPNPayment': False, 'AllowOnlinePayment': False, 'AllowOnlineCreditCardPayment': False, 'AllowOnlineACHPayment': False, 'domain': 'QBO', 'sparse': False, 'Id': '3', 'SyncToken': '1', 'MetaData': {'CreateTime': '2020-02-19T07:14:35-08:00', 'LastUpdatedTime': '2020-02-19T07:45:32-08:00'}, 'CustomField': [], 'DocNumber': '1003', 'TxnDate': '2020-02-09', 'DepartmentRef': {'value': '2', 'name': 'Paris 11e'}, 'CurrencyRef': {'value': 'EUR', 'name': 'Euro'}, 'LinkedTxn': [], 'Line': [{'Id': '1', 'LineNum': 1, 'Amount': 50.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '5', 'name': 'Chocolat au lait'}, 'UnitPrice': 5, 'Qty': 10, 'ItemAccountRef': {'value': '1', 'name': '70710000 Ventes de Marchandises (ou groupe) A 20%'}, 'TaxCodeRef': {'value': '31'}}}, {'Id': '2', 'LineNum': 2, 'Description': 'Frandises 100g', 'Amount': 400.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '1', 'name': 'Ventes bonbons'}, 'UnitPrice': 10, 'Qty': 40, 'ItemAccountRef': {'value': '71', 'name': '70110000 Ventes de Produits finis (ou groupe) A 20%'}, 'TaxCodeRef': {'value': '31'}}}, {'Id': '3', 'LineNum': 3, 'Amount': 200.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '7', 'name': 'Gateaux'}, 'UnitPrice': 20, 'Qty': 10, 'ItemAccountRef': {'value': '1', 'name': '70710000 Ventes de Marchandises (ou groupe) A 20%'}, 'TaxCodeRef': {'value': '31'}}}, {'Id': '4', 'LineNum': 4, 'Amount': 200.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '10', 'name': 'Pain tradition'}, 'UnitPrice': 2, 'Qty': 100, 'ItemAccountRef': {'value': '1', 'name': '70710000 Ventes de Marchandises (ou groupe) A 20%'}, 'TaxCodeRef': {'value': '31'}}}, {'Amount': 850.0, 'DetailType': 'SubTotalLineDetail', 'SubTotalLineDetail': {}}, {'Amount': 0, 'DetailType': 'DiscountLineDetail', 'DiscountLineDetail': {'PercentBased': False}}], 'TxnTaxDetail': {'TotalTax': 170.0, 'TaxLine': [{'Amount': 170.0, 'DetailType': 'TaxLineDetail', 'TaxLineDetail': {'TaxRateRef': {'value': '24'}, 'PercentBased': True, 'TaxPercent': 20, 'NetAmountTaxable': 850.0}}]}, 'TransactionLocationType': 'WithinFrance', 'CustomerRef': {'value': '16', 'name': 'La\xa0fromagerie'}, 'BillAddr': {'Id': '16', 'Line1': 'La\xa0fromagerie\xa0', 'Line2': '64, rue de Seine', 'Line3': 'Paris  75006'}, 'ShipAddr': {'Id': '15', 'Line1': '64, rue de Seine', 'City': 'Paris', 'PostalCode': '75006\xa0', 'Lat': '48.8532188', 'Long': '2.3368985'}, 'FreeFormAddress': True, 'ClassRef': {'value': '301200000000000002082', 'name': 'Magasins'}, 'SalesTermRef': {'value': '3'}, 'DueDate': '2020-03-10', 'GlobalTaxCalculation': 'TaxExcluded', 'TotalAmt': 1020.0, 'PrintStatus': 'NotSet', 'EmailStatus': 'NotSet', 'Balance': 1020.0, 'DiscountAmt': 0}, {'AllowIPNPayment': False, 'AllowOnlinePayment': False, 'AllowOnlineCreditCardPayment': False, 'AllowOnlineACHPayment': False, 'domain': 'QBO', 'sparse': False, 'Id': '2', 'SyncToken': '1', 'MetaData': {'CreateTime': '2020-02-19T07:13:09-08:00', 'LastUpdatedTime': '2020-02-19T07:19:09-08:00'}, 'CustomField': [], 'DocNumber': '1002', 'TxnDate': '2020-01-11', 'CurrencyRef': {'value': 'EUR', 'name': 'Euro'}, 'LinkedTxn': [{'TxnId': '6', 'TxnType': 'Payment'}], 'Line': [{'Id': '1', 'LineNum': 1, 'Amount': 200.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '10', 'name': 'Pain tradition'}, 'UnitPrice': 2, 'Qty': 100, 'ItemAccountRef': {'value': '1', 'name': '70710000 Ventes de Marchandises (ou groupe) A 20%'}, 'TaxCodeRef': {'value': '31'}}}, {'Id': '2', 'LineNum': 2, 'Amount': 200.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '7', 'name': 'Gateaux'}, 'UnitPrice': 20, 'Qty': 10, 'ItemAccountRef': {'value': '1', 'name': '70710000 Ventes de Marchandises (ou groupe) A 20%'}, 'TaxCodeRef': {'value': '31'}}}, {'Id': '3', 'LineNum': 3, 'Amount': 250.0, 'DetailType': 'SalesItemLineDetail', 'SalesItemLineDetail': {'DiscountAmt': 0, 'ItemRef': {'value': '5', 'name': 'Chocolat au lait'}, 'UnitPrice': 5, 'Qty': 50, 'ItemAccountRef': {'value': '1', 'name': '70710000 Ventes de Marchandises (ou groupe) A 20%'}, 'TaxCodeRef': {'value': '31'}}}, {'Amount': 650.0, 'DetailType': 'SubTotalLineDetail', 'SubTotalLineDetail': {}}, {'Amount': 0, 'DetailType': 'DiscountLineDetail', 'DiscountLineDetail': {'PercentBased': False}}], 'TxnTaxDetail': {'TotalTax': 130.0, 'TaxLine': [{'Amount': 130.0, 'DetailType': 'TaxLineDetail', 'TaxLineDetail': {'TaxRateRef': {'value': '24'}, 'PercentBased': True, 'TaxPercent': 20, 'NetAmountTaxable': 650.0}}]}, 'TransactionLocationType': 'WithinFrance', 'CustomerRef': {'value': '15', 'name': 'Franprix Supermarche'}, 'BillAddr': {'Id': '14', 'Line1': "58 Rue d'Auteuil\xa0", 'City': 'Paris', 'PostalCode': '75009', 'Lat': '48.8481548', 'Long': '2.2620632'}, 'ShipAddr': {'Id': '14', 'Line1': "58 Rue d'Auteuil\xa0", 'City': 'Paris', 'PostalCode': '75009', 'Lat': '48.8481548', 'Long': '2.2620632'}, 'FreeFormAddress': True, 'SalesTermRef': {'value': '3'}, 'DueDate': '2020-02-10', 'GlobalTaxCalculation': 'TaxExcluded', 'TotalAmt': 780.0, 'PrintStatus': 'NotSet', 'EmailStatus': 'NotSet', 'Balance': 0, 'DiscountAmt': 0}], 'startPosition': 1, 'maxResults': 10, 'totalCount': 10}, 'time': '2020-03-04T07:02:54.354-08:00'}
