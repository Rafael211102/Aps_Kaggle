# API de Dados de Ações da Apple (AAPL)

Esta é uma API RESTful básica construída com **FastAPI** e **Python**, conforme solicitado, utilizando o dataset histórico de ações da Apple (AAPL).

A API implementa:
*   **Autenticação JWT** (JSON Web Token) para proteger os endpoints.
*   **Endpoints CRUD** (Create, Read, Update, Delete) para manipulação dos dados.
*   **Paginação** no endpoint de leitura de todos os registros.

## Estrutura do Projeto

```
apple_stock_api/
├── main.py       # Lógica principal da API, endpoints e carregamento de dados.
├── auth.py       # Lógica de autenticação JWT e modelos de usuário.
├── AAPL          # Arquivo de dados CSV (copiado para o diretório de upload).
└── README.md     # Este arquivo.
```

## Requisitos

Para rodar a API, você precisará ter o Python 3.8+ instalado e as seguintes bibliotecas:

```bash
pip install fastapi uvicorn pandas python-multipart python-jose[cryptography]
```

## Como Rodar a API

1.  **Navegue** até o diretório do projeto:
    ```bash
    cd /home/ubuntu/apple_stock_api
    ```
2.  **Inicie** o servidor Uvicorn:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    O servidor estará acessível em `http://0.0.0.0:8000`.

## Credenciais de Teste

A API utiliza um usuário de teste embutido para a autenticação JWT:

| Campo | Valor |
| :--- | :--- |
| **Username** | `aluno_unip` |
| **Password** | `unip2025` |

## Endpoints da API

A documentação interativa completa (Swagger UI) estará disponível em `http://0.0.0.0:8000/docs`.

### 1. Autenticação

| Método | Caminho | Descrição |
| :--- | :--- | :--- |
| `POST` | `/token` | Gera um token de acesso JWT. Requer `username` e `password` no corpo da requisição (form-urlencoded). |
| `GET` | `/users/me/` | Retorna informações do usuário autenticado (requer token). |

### 2. Dados de Ações (Requer Autenticação)

| Método | Caminho | Descrição |
| :--- | :--- | :--- |
| `GET` | `/stocks` | **Leitura com Paginação.** Retorna uma lista de registros. Parâmetros de query: `page` (padrão 1) e `size` (padrão 10). |
| `GET` | `/stocks/{date_str}` | **Leitura por Data.** Retorna o registro de ações para uma data específica (ex: `1980-12-12 00:00:00-05:00`). |
| `POST` | `/stocks` | **Criação.** Adiciona um novo registro de ações. |
| `PUT` | `/stocks/{date_str}` | **Atualização Completa.** Substitui um registro existente pela data. |
| `PATCH` | `/stocks/{date_str}` | **Atualização Parcial.** Atualiza campos específicos de um registro existente pela data. |
| `DELETE` | `/stocks/{date_str}` | **Exclusão.** Remove um registro de ações pela data. |

## Observações Técnicas

*   **Carregamento de Dados:** O arquivo `AAPL` (CSV) é carregado na memória usando a biblioteca `pandas` na inicialização da aplicação.
*   **Chave Primária:** A coluna `Date` é usada como chave primária para os endpoints CRUD.
*   **Segurança:** A senha de teste (`unip2025`) está simulada no arquivo `auth.py` para fins de demonstração. Em um projeto real, seria necessário usar hash de senha (ex: `bcrypt`) e um banco de dados persistente.
*   **Formato da Data:** O formato da data no dataset é `YYYY-MM-DD HH:MM:SS-TZ`, e é usado como identificador nos endpoints.
