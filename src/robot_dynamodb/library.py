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
