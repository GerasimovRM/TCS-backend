import requests

headers = {"Authorization":
               "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2a19pZCI6IjUzOTA1NTg1MiIsImlzX2FkbWluIjpmYWxzZSwiaXNfdGVhY2hlciI6ZmFsc2UsImV4cCI6MTY1NTQ2MDA3NX0.OitR6ppO6Jwaul4_3hvC8cuPTEE_TI0ymgH8pDCvzaM"}
params = {"user_id": 7}
response = requests.get("http://127.0.0.1:5000/user", headers=headers, params=params)
print(response.status_code, response.json())