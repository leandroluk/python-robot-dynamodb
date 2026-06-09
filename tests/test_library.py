import pytest
from unittest.mock import MagicMock
from robot_dynamodb.library import DynamoDbLibrary


@pytest.fixture
def lib(mocker) -> DynamoDbLibrary:
    mock_resource = mocker.MagicMock()
    mocker.patch("robot_dynamodb.library.boto3.resource", return_value=mock_resource)
    instance = DynamoDbLibrary()
    instance.connect_to_dynamodb(
        "http://localhost:4566", table_prefix="test_", table_postfix="_v1"
    )
    return instance


@pytest.fixture
def mock_table(lib) -> MagicMock:
    return lib._resource.Table.return_value


class TestConnection:
    def test_connect_passes_correct_args(self, mocker):
        mock_boto = mocker.patch("robot_dynamodb.library.boto3.resource")
        lib = DynamoDbLibrary()
        lib.connect_to_dynamodb("http://localhost:4566", region="sa-east-1")
        mock_boto.assert_called_once_with(
            "dynamodb",
            endpoint_url="http://localhost:4566",
            region_name="sa-east-1",
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )

    def test_connect_stores_prefix_and_postfix(self, mocker):
        mocker.patch("robot_dynamodb.library.boto3.resource")
        lib = DynamoDbLibrary()
        lib.connect_to_dynamodb(
            "http://localhost:4566", table_prefix="dev_", table_postfix="_v2"
        )
        assert lib._table_prefix == "dev_"
        assert lib._table_postfix == "_v2"

    def test_disconnect_clears_state(self, lib):
        lib.disconnect_from_dynamodb()
        assert lib._resource is None
        assert lib._table_prefix == ""
        assert lib._table_postfix == ""

    def test_get_resource_without_connect_raises(self):
        lib = DynamoDbLibrary()
        with pytest.raises(RuntimeError, match="Not connected"):
            lib._get_resource()

    def test_table_name_uses_prefix_and_postfix(self, lib):
        lib._table("orders")
        lib._resource.Table.assert_called_with("test_orders_v1")


class TestCRUD:
    def test_create_item_calls_put_and_returns_item(self, lib, mock_table):
        item = {"id": "1", "name": "test"}
        result = lib.create_dynamodb_item("orders", item)
        lib._resource.Table.assert_called_with("test_orders_v1")
        mock_table.put_item.assert_called_once_with(Item=item)
        assert result == item

    def test_get_item_returns_item(self, lib, mock_table):
        mock_table.get_item.return_value = {"Item": {"id": "1"}}
        result = lib.get_dynamodb_item("orders", {"id": "1"})
        mock_table.get_item.assert_called_once_with(Key={"id": "1"})
        assert result == {"id": "1"}

    def test_get_item_returns_none_when_missing(self, lib, mock_table):
        mock_table.get_item.return_value = {}
        assert lib.get_dynamodb_item("orders", {"id": "999"}) is None

    def test_update_item_without_names(self, lib, mock_table):
        mock_table.update_item.return_value = {}
        lib.update_dynamodb_item("orders", {"id": "1"}, "SET #s = :s", {":s": "shipped"})
        mock_table.update_item.assert_called_once_with(
            Key={"id": "1"},
            UpdateExpression="SET #s = :s",
            ExpressionAttributeValues={":s": "shipped"},
        )

    def test_update_item_with_names(self, lib, mock_table):
        mock_table.update_item.return_value = {}
        lib.update_dynamodb_item(
            "orders", {"id": "1"}, "SET #s = :s", {":s": "ok"}, {"#s": "status"}
        )
        mock_table.update_item.assert_called_once_with(
            Key={"id": "1"},
            UpdateExpression="SET #s = :s",
            ExpressionAttributeValues={":s": "ok"},
            ExpressionAttributeNames={"#s": "status"},
        )

    def test_delete_item(self, lib, mock_table):
        lib.delete_dynamodb_item("orders", {"id": "1"})
        mock_table.delete_item.assert_called_once_with(Key={"id": "1"})
