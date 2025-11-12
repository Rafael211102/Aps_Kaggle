import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    Token,
    FAKE_USERS_DB,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    User
)

# --- Configuração da API ---
app = FastAPI(
    title="API de Dados de Ações da Apple (AAPL)",
    description="API segura com JWT e endpoints CRUD (GET, POST, PUT, PATCH, DELETE) com paginação, utilizando dados históricos da Apple (AAPL) do Kaggle.",
    version="1.0.0"
)

# --- Modelos Pydantic para o Dataset ---
class StockData(BaseModel):
    Date: datetime = Field(..., example="2024-12-31 00:00:00-05:00")
    Open: float = Field(..., example=170.00)
    High: float = Field(..., example=172.50)
    Low: float = Field(..., example=169.00)
    Close: float = Field(..., example=171.25)
    Volume: int = Field(..., example=100000000)

class StockDataCreate(BaseModel):
    Date: str = Field(..., example="2024-12-31 00:00:00-05:00", description="Data no formato ISO 8601")
    Open: float = Field(..., example=170.00)
    High: float = Field(..., example=172.50)
    Low: float = Field(..., example=169.00)
    Close: float = Field(..., example=171.25)
    Volume: int = Field(..., example=100000000)

class StockDataUpdate(BaseModel):
    Open: Optional[float] = Field(None, example=170.00)
    High: Optional[float] = Field(None, example=172.50)
    Low: Optional[float] = Field(None, example=169.00)
    Close: Optional[float] = Field(None, example=171.25)
    Volume: Optional[int] = Field(None, example=100000000)

# --- Carregamento e Preparação dos Dados ---
DATA_FILE = "AAPL.csv"
try:
    # Carrega o CSV, define a coluna 'Date' como índice e a converte para datetime
    df = pd.read_csv(DATA_FILE, index_col='Date', parse_dates=True)
    # Converte o índice para string para facilitar a serialização JSON
    df.index = df.index.astype(str)
    # Converte o DataFrame para um dicionário de registros (lista de dicionários)
    stock_data_records = df.reset_index().to_dict('records')
    print(f"Dados carregados com sucesso. Total de registros: {len(stock_data_records)}")
except Exception as e:
    print(f"Erro ao carregar os dados: {e}")
    stock_data_records = []

# --- Endpoint de Autenticação ---
@app.post("/token", response_model=Token, tags=["Autenticação"])
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(FAKE_USERS_DB, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User, tags=["Autenticação"])
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

# --- Endpoints CRUD de Dados de Ações ---

@app.get("/stocks", response_model=List[StockData], tags=["Dados de Ações"])
async def get_stocks(
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Tamanho da página")
):
    """
    Retorna dados de ações da Apple com paginação.
    Requer autenticação JWT.
    """
    if not stock_data_records:
        raise HTTPException(status_code=500, detail="Dados não carregados.")

    start = (page - 1) * size
    end = start + size

    if start >= len(stock_data_records):
        return [] # Retorna lista vazia se a página estiver fora do limite

    return stock_data_records[start:end]

@app.get("/stocks/{date_str}", response_model=StockData, tags=["Dados de Ações"])
async def get_stock_by_date(
    current_user: Annotated[User, Depends(get_current_active_user)],
    date_str: str
):
    """
    Retorna dados de ações para uma data específica.
    Requer autenticação JWT.
    """
    try:
        # Tenta encontrar o registro pela data (que é o índice original)
        record = next(item for item in stock_data_records if item["Date"] == date_str)
        return record
    except StopIteration:
        raise HTTPException(status_code=404, detail="Registro não encontrado para a data especificada.")

@app.post("/stocks", response_model=StockData, status_code=status.HTTP_201_CREATED, tags=["Dados de Ações"])
async def create_stock_data(
    current_user: Annotated[User, Depends(get_current_active_user)],
    stock_data: StockDataCreate
):
    """
    Adiciona um novo registro de dados de ações.
    Requer autenticação JWT.
    """
    # Verifica se a data já existe
    if any(item["Date"] == stock_data.Date for item in stock_data_records):
        raise HTTPException(status_code=400, detail="Registro para esta data já existe.")

    new_record = stock_data.model_dump()
    # Adiciona o novo registro ao início da lista (simulando um novo dado)
    stock_data_records.insert(0, new_record)
    return new_record

@app.put("/stocks/{date_str}", response_model=StockData, tags=["Dados de Ações"])
async def update_stock_data(
    current_user: Annotated[User, Depends(get_current_active_user)],
    date_str: str,
    stock_data: StockDataCreate
):
    """
    Substitui completamente um registro de dados de ações existente.
    Requer autenticação JWT.
    """
    try:
        index = next(i for i, item in enumerate(stock_data_records) if item["Date"] == date_str)
        updated_record = stock_data.model_dump()
        stock_data_records[index] = updated_record
        return updated_record
    except StopIteration:
        raise HTTPException(status_code=404, detail="Registro não encontrado para a data especificada.")

@app.patch("/stocks/{date_str}", response_model=StockData, tags=["Dados de Ações"])
async def partial_update_stock_data(
    current_user: Annotated[User, Depends(get_current_active_user)],
    date_str: str,
    stock_data: StockDataUpdate
):
    """
    Atualiza parcialmente um registro de dados de ações existente.
    Requer autenticação JWT.
    """
    try:
        index = next(i for i, item in enumerate(stock_data_records) if item["Date"] == date_str)
        current_record = stock_data_records[index]
        update_data = stock_data.model_dump(exclude_unset=True)
        current_record.update(update_data)
        return current_record
    except StopIteration:
        raise HTTPException(status_code=404, detail="Registro não encontrado para a data especificada.")

@app.delete("/stocks/{date_str}", status_code=status.HTTP_204_NO_CONTENT, tags=["Dados de Ações"])
async def delete_stock_data(
    current_user: Annotated[User, Depends(get_current_active_user)],
    date_str: str
):
    """
    Deleta um registro de dados de ações.
    Requer autenticação JWT.
    """
    global stock_data_records
    initial_count = len(stock_data_records)
    stock_data_records = [item for item in stock_data_records if item["Date"] != date_str]

    if len(stock_data_records) == initial_count:
        raise HTTPException(status_code=404, detail="Registro não encontrado para a data especificada.")
    return
