import requests

# Altere a URL base para o endereço local do seu servidor Uvicorn
API_URL = "http://127.0.0.1:8000/"
TOKEN_URL = f"{API_URL}/token"

# --- 1. Obter Token de Acesso ---
data = {
    "username": "aluno_unip",
    "password": "unip2025"
}

print("--- 1. Obtendo Token de Acesso ---")
response = requests.post(TOKEN_URL, data=data)

if response.status_code == 200:
    token_data = response.json()
    TOKEN = token_data['access_token']
    HEADERS = {
        "Authorization": f"Bearer {TOKEN}"
    }
    print(f"TOKEN OBTIDO com sucesso.")
else:
    print(f"FALHA ao obter token: Status Code {response.status_code}")
    print(f"Response: {response.text}")
    exit() # Interrompe se não conseguir o token

# --- 2. Testar GET /stocks (com paginação) ---
print("\n--- 2. Testando GET /stocks (página 1, tamanho 5) ---")
response_get_stocks = requests.get(f"{API_URL}/stocks?page=1&size=5", headers=HEADERS)
if response_get_stocks.status_code == 200:
    data = response_get_stocks.json()
    print(f"Sucesso. Registros recebidos: {len(data)}")
    # Pegar a data do primeiro registro para o próximo teste
    first_date = data[0]['Date']
    print(f"Primeira data: {first_date}")
else:
    print(f"Falha no GET /stocks: Status Code {response_get_stocks.status_code}")
    print(f"Response: {response_get_stocks.text}")
    first_date = None

# --- 3. Testar GET /stocks/{date_str} ---
if first_date:
    # A data precisa ser URL-encoded, mas o requests faz isso automaticamente
    print(f"\n--- 3. Testando GET /stocks/{first_date} ---")
    response_get_by_date = requests.get(f"{API_URL}/stocks/{first_date}", headers=HEADERS)
    if response_get_by_date.status_code == 200:
        print("Sucesso. Registro recebido.")
        # print(response_get_by_date.json()) # Descomente para ver o registro completo
    else:
        print(f"Falha no GET /stocks/{{date_str}}: Status Code {response_get_by_date.status_code}")
        print(f"Response: {response_get_by_date.text}")

# --- 4. Testar POST /stocks (Criação) ---
new_date = "2025-01-01 00:00:00-05:00"
new_data = {
    "Date": new_date,
    "Open": 180.00,
    "High": 182.50,
    "Low": 179.00,
    "Close": 181.25,
    "Volume": 150000000
}
print(f"\n--- 4. Testando POST /stocks (Criação para {new_date}) ---")
response_post = requests.post(f"{API_URL}/stocks", headers=HEADERS, json=new_data)
if response_post.status_code == 201:
    print("Sucesso. Registro criado.")
else:
    print(f"Falha no POST /stocks: Status Code {response_post.status_code}")
    print(f"Response: {response_post.text}")

# --- 5. Testar PATCH /stocks/{date_str} (Atualização Parcial) ---
update_data = {
    "Close": 185.00
}
print(f"\n--- 5. Testando PATCH /stocks/{new_date} (Atualização Parcial) ---")
response_patch = requests.patch(f"{API_URL}/stocks/{new_date}", headers=HEADERS, json=update_data)
if response_patch.status_code == 200:
    print("Sucesso. Registro atualizado parcialmente.")
    # print(response_patch.json()) # Descomente para ver o registro atualizado
else:
    print(f"Falha no PATCH /stocks/{{date_str}}: Status Code {response_patch.status_code}")
    print(f"Response: {response_patch.text}")

# --- 6. Testar DELETE /stocks/{date_str} ---
print(f"\n--- 6. Testando DELETE /stocks/{new_date} ---")
response_delete = requests.delete(f"{API_URL}/stocks/{new_date}", headers=HEADERS)
if response_delete.status_code == 204:
    print("Sucesso. Registro deletado.")
else:
    print(f"Falha no DELETE /stocks/{{date_str}}: Status Code {response_delete.status_code}")
    print(f"Response: {response_delete.text}")

# --- 7. Testar GET /stocks/{date_str} (Verificar exclusão) ---
print(f"\n--- 7. Testando GET /stocks/{new_date} (Verificar exclusão) ---")
response_verify_delete = requests.get(f"{API_URL}/stocks/{new_date}", headers=HEADERS)
if response_verify_delete.status_code == 404:
    print("Sucesso. Registro não encontrado (excluído).")
else:
    print(f"Falha na verificação de exclusão: Status Code {response_verify_delete.status_code}")
    print(f"Response: {response_verify_delete.text}")