# robot-dynamodb

Robot Framework library for DynamoDB. Works with LocalStack and AWS.

## Installation

```bash
pip install robot-dynamodb
```

## Usage

```robot
*** Settings ***
Library    robot_dynamodb.DynamoDbLibrary

Suite Setup       Connect To DynamoDB
...    endpoint_url=http://localhost:4566
...    region=sa-east-1
...    table_prefix=dev_
...    table_postfix=_v1
Suite Teardown    Disconnect From DynamoDB

Test Setup        Truncate DynamoDB Table    orders
Test Teardown     Truncate DynamoDB Table    orders

*** Test Cases ***
Pedido deve ser persistido
    Batch Write DynamoDB Items    orders    ${seed_items}
    Item Should Exist In DynamoDB    orders    {"id": "123"}
```

## Keywords

| Keyword | Descrição |
|---|---|
| `Connect To DynamoDB` | Cria conexão boto3 |
| `Disconnect From DynamoDB` | Limpa estado |
| `Create DynamoDB Item` | Insere item (`put_item`) |
| `Get DynamoDB Item` | Busca por chave |
| `Update DynamoDB Item` | Atualiza atributos |
| `Delete DynamoDB Item` | Remove por chave |
| `Scan DynamoDB Table` | Lista todos os items |
| `Query DynamoDB Table` | Busca por partition key |
| `Truncate DynamoDB Table` | Deleta todos os items |
| `Batch Write DynamoDB Items` | Insere lista de items |
| `Item Should Exist In DynamoDB` | Falha se item não encontrado |
| `Item Should Not Exist In DynamoDB` | Falha se item encontrado |

## Connect To DynamoDB Parameters

| Parâmetro | Default | Descrição |
|---|---|---|
| `endpoint_url` | — | URL do DynamoDB / LocalStack |
| `region` | `us-east-1` | AWS region |
| `table_prefix` | `""` | Prefixo do nome da tabela |
| `table_postfix` | `""` | Sufixo do nome da tabela |
| `aws_access_key_id` | `test` | AWS / LocalStack key |
| `aws_secret_access_key` | `test` | AWS / LocalStack secret |
