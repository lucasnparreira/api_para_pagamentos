# API de Gerenciamento de Pagamentos

Esta API foi desenvolvida para gerenciar usuários, pagamentos e transações. É possível criar, ler, atualizar e excluir usuários, pagamentos e transações, além de realizar o login de um usuário para gerar uma chave de API (API Key).

## Tecnologias
- Python 3
- Flask
- SQLAlchemy
- SQLite
- JWT (para a chave da API)

## Como rodar a API
1. Clone este repositório.
2. Instale as dependências com `pip install -r requirements.txt`.
3. Execute a aplicação com `python app.py`.
4. Acesse a API na URL `http://127.0.0.1:5000/`.

---

## Endpoints

### **/register**
**Método:** `POST`

**Descrição:** Cadastra um novo usuário.

**Corpo da requisição (JSON):**
```json
{
    "name": "Lucas Parreira",
    "email": "lnparreiraa@example.com",
    "password": "123456"
}
```

### **/login**
**Método:** POST

**Descrição:** Realiza o login de um usuário, gerando uma chave de API (API Key).

```json
Corpo da requisição (JSON):

{
    "email": "lnparreiraa@example.com",
    "password": "123456"
}
```

### **/logout**
**Método:** POST

**Descrição:** Realiza o logout de um usuário, removendo a chave de API.

**Cabeçalho (x-api-key):** <insira a api-key gerada no cabeçalho (head)>

Resposta (200 OK):
```json
{
    "message": "Logged out successfully"
}
```

### **/users**
**Método:** GET

**Descrição:** Lista todos os usuários.

**Cabeçalho (x-api-key):** <insira a api-key gerada no cabeçalho (head)>

Resposta (200 OK):
```json
[
    {
        "id": 1,
        "name": "Lucas Parreira",
        "email": "lnparreiraa@example.com",
        "api_key": "a8d31d35-b4a7-4ff1-a3ef-f8760c1c0000",
        "api_key_expiration": "2025-03-07T10:00:00"
    },
    {
        "id": 2,
        "name": "Maria Oliveira",
        "email": "maria.oliveira@example.com",
        "api_key": "bb9d9b57-c4d1-4f5d-9c6a-882377fef3fd",
        "api_key_expiration": "2025-03-07T10:00:00"
    }
]
```

**Método:** POST

**Descrição:** Cria um novo usuário.

Corpo da requisição (JSON):
```json
{
    "name": "João Silva",
    "email": "joao.silva@example.com",
    "password": "password123"
}
```
Resposta (201 Created):
```json
{
    "message": "User created successfully"
}
```

**Método:** PUT

**Descrição:** Atualiza um usuário existente.

Corpo da requisição (JSON):
```json
{
    "name": "João Silva Atualizado",
    "email": "joao.silva.updated@example.com"
}
```
Resposta (200 OK):
```json
{
    "message": "User updated successfully"
}
```

**Método:** DELETE

**Descrição:** Exclui um usuário específico.

Resposta (200 OK):
```json
{
    "message": "User deleted successfully"
}
```

### **/users/id**
**Método:** GET

**Descrição:** Recupera informações de um usuário específico.

**Cabeçalho (x-api-key):** <insira a api-key gerada no cabeçalho (head)>

Resposta (200 OK):
```json
{
    "id": 1,
    "name": "Lucas Parreira",
    "email": "lnparreiraa@example.com",
    "api_key": "a8d31d35-b4a7-4ff1-a3ef-f8760c1c0000",
    "api_key_expiration": "2025-03-07T10:00:00"
}
```

### **/transactions**
**Método:** GET

**Descrição:** Lista todas as transações.

**Cabeçalho (x-api-key):** <insira a api-key gerada no cabeçalho (head)>

Resposta (200 OK):
```json
[
    {
        "id": 1,
        "payment_id": 1,
        "transaction_date": "2025-03-07T10:00:00",
        "transaction_type": "payment"
    },
    {
        "id": 2,
        "payment_id": 2,
        "transaction_date": "2025-03-07T12:00:00",
        "transaction_type": "refund"
    }
]
```

**Método:** POST

**Descrição:** Cria uma nova transação.

Corpo da requisição (JSON):
```json
{
    "payment_id": 1,
    "transaction_date": "2025-03-07T10:00:00",
    "transaction_type": "payment"
}
```
Resposta (201 Created):
```json
{
    "message": "Transaction created successfully"
}
```

**Método:** PUT

**Descrição:** Atualiza uma transação existente.

Corpo da requisição (JSON):
```json
{
    "transaction_type": "refund"
}
```
Resposta (200 OK):
```json
{
    "message": "Transaction updated successfully"
}
```

**Método:** DELETE

**Descrição:** Exclui uma transação específica.

Resposta (200 OK):
```json
{
    "message": "Transaction deleted successfully"
}
```

### **/transactions/id**
**Método:** GET

**Descrição:** Recupera informações de uma transação específica.

**Cabeçalho (x-api-key):** <insira a api-key gerada no cabeçalho (head)>

Resposta (200 OK):
```json
{
    "id": 1,
    "payment_id": 1,
    "transaction_date": "2025-03-07T10:00:00",
    "transaction_type": "payment"
}
```

### **/payments**
**Método:** GET

**Descrição:** Lista todos os pagamentos.

**Cabeçalho (x-api-key):** <insira a api-key gerada no cabeçalho (head)>

Resposta (200 OK):
```json
[
    {
        "id": 1,
        "user_id": 1,
        "amount": 100.00,
        "status": "completed"
    },
    {
        "id": 2,
        "user_id": 2,
        "amount": 50.00,
        "status": "pending"
    }
]
```

**Método:** POST

**Descrição:** Cria um novo pagamento.

Corpo da requisição (JSON):
```json
{
    "user_id": 1,
    "amount": 100.00,
    "status": "completed"
}
```
Resposta (201 Created):
```json
{
    "message": "Payment created successfully"
}
```

**Método:** PUT

**Descrição:** Atualiza um pagamento existente.

Corpo da requisição (JSON):
```json
{
    "amount": 120.00,
    "status": "completed"
}
```
Resposta (200 OK):
```json
{
    "message": "Payment updated successfully"
}
```

**Método:** DELETE

**Descrição:** Exclui um pagamento específico.

Resposta (200 OK):
```json
{
    "message": "Payment deleted successfully"
}
```

### **/payments/id**
**Método:** GET

**Descrição:** Recupera informações de um pagamento específico.

**Cabeçalho (x-api-key):** <insira a api-key gerada no cabeçalho (head)>

Resposta (200 OK):
```json
{
    "id": 1,
    "user_id": 1,
    "amount": 100.00,
    "status": "completed"
}
```