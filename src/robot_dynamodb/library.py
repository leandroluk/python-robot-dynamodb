from typing import Any, Protocol, cast

import boto3
from robot.api.deco import keyword, library


class DynamoDBTable(Protocol):
    key_schema: list[dict[str, str]]

    def put_item(self, Item: dict[str, Any], **kwargs: Any) -> dict[str, Any]: ...
    def get_item(self, Key: dict[str, Any], **kwargs: Any) -> dict[str, Any]: ...
    def update_item(self, Key: dict[str, Any], **kwargs: Any) -> dict[str, Any]: ...
    def delete_item(self, Key: dict[str, Any], **kwargs: Any) -> dict[str, Any]: ...
    def scan(self, **kwargs: Any) -> dict[str, Any]: ...
    def query(self, **kwargs: Any) -> dict[str, Any]: ...
    def batch_writer(self) -> Any: ...


class DynamoDBResource(Protocol):
    def Table(self, name: str) -> DynamoDBTable: ...


@library(scope="SUITE")
class DynamoDbLibrary:
    _resource: DynamoDBResource | None
    _table_prefix: str
    _table_postfix: str

    def __init__(self) -> None:
        self._resource = None
        self._table_prefix = ""
        self._table_postfix = ""

    def _get_resource(self) -> DynamoDBResource:
        if self._resource is None:
            raise RuntimeError("Not connected. Call 'Connect To DynamoDB' first.")
        return self._resource

    def _table(self, table_name: str) -> DynamoDBTable:
        return self._get_resource().Table(
            f"{self._table_prefix}{table_name}{self._table_postfix}"
        )

    @keyword
    def connect_to_dynamodb(
        self,
        endpoint_url: str,
        region: str = "us-east-1",
        table_prefix: str = "",
        table_postfix: str = "",
        aws_access_key_id: str = "test",
        aws_secret_access_key: str = "test",
    ) -> None:
        self._table_prefix = table_prefix
        self._table_postfix = table_postfix
        self._resource = cast(
            DynamoDBResource,
            boto3.resource(
                "dynamodb",
                endpoint_url=endpoint_url,
                region_name=region,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            ),
        )

    @keyword
    def disconnect_from_dynamodb(self) -> None:
        self._resource = None
        self._table_prefix = ""
        self._table_postfix = ""

    @keyword
    def create_dynamodb_item(self, table_name: str, item: dict[str, Any]) -> dict[str, Any]:
        self._table(table_name).put_item(Item=item)
        return item

    @keyword
    def get_dynamodb_item(self, table_name: str, key: dict[str, Any]) -> dict[str, Any] | None:
        return self._table(table_name).get_item(Key=key).get("Item")

    @keyword
    def update_dynamodb_item(
        self,
        table_name: str,
        key: dict[str, Any],
        update_expression: str,
        expression_attribute_values: dict[str, Any],
        expression_attribute_names: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "Key": key,
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": expression_attribute_values,
        }
        if expression_attribute_names:
            kwargs["ExpressionAttributeNames"] = expression_attribute_names
        return self._table(table_name).update_item(**kwargs)

    @keyword
    def delete_dynamodb_item(self, table_name: str, key: dict[str, Any]) -> None:
        self._table(table_name).delete_item(Key=key)

    @keyword
    def scan_dynamodb_table(self, table_name: str) -> list[dict[str, Any]]:
        return self._table(table_name).scan().get("Items", [])

    @keyword
    def query_dynamodb_table(
        self,
        table_name: str,
        key_condition_expression: str,
        expression_attribute_values: dict[str, Any],
        expression_attribute_names: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        kwargs: dict[str, Any] = {
            "KeyConditionExpression": key_condition_expression,
            "ExpressionAttributeValues": expression_attribute_values,
        }
        if expression_attribute_names:
            kwargs["ExpressionAttributeNames"] = expression_attribute_names
        return self._table(table_name).query(**kwargs).get("Items", [])

    @keyword
    def truncate_dynamodb_table(self, table_name: str) -> None:
        table = self._table(table_name)
        key_names = {k["AttributeName"] for k in table.key_schema}
        items = table.scan().get("Items", [])
        with table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={k: v for k, v in item.items() if k in key_names})

    @keyword
    def batch_write_dynamodb_items(
        self, table_name: str, items: list[dict[str, Any]]
    ) -> None:
        table = self._table(table_name)
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)
