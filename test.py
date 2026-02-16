
import requests

url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
payload = {
  "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjYwMjE2MTIzODI4",
  "BusinessShortCode": "174379",
  "Timestamp": "20260216123828",
  "Amount": "1",
  "PartyA": "254708374149",
  "PartyB": "174379",
  "TransactionType": "CustomerPayBillOnline",
  "PhoneNumber": "254708374149",
  "TransactionDesc": "Test",
  "AccountReference": "Test",
  "CallBackURL": "https://mydomain.com/mpesa-express-simulate/"
}

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer <ACCESS_TOKEN>"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
