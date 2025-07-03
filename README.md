**GeyserClient: Async Python gRPC Client for Solana Geyser (Yellowstone)**

A lightweight, asynchronous Python client for interacting with the Solana Geyser (Yellowstone) gRPC API. This library provides an easy-to-use interface to subscribe to account updates, query blockchain state, and perform health checks via gRPC.

---

## Features

- **Async API**: Built on `grpc.aio` and `asyncio` for efficient, non-blocking I/O.
- **Subscription Management**: Subscribe to account updates, automatically queueing and yielding responses.
- **Health Check**: Simple `ping` method to verify connectivity and responsiveness.
- **Chain State Queries**: Fetch the latest blockhash, slot, and block height with desired commitment levels.
- **Blockhash Validation**: Validate blockhashes against the current ledger state.
- **Version Info**: Retrieve Geyser server version.

---

## Installation

```sh
# Install from PyPI (if published)
pip install solana-geyser-client

# Or install directly from GitHub
pip install git+https://github.com/<your-org>/solana-geyser-client.git
```

## Requirements

- Python 3.8+
- `grpcio` and `grpcio-tools`
- `protobuf` (matching `.proto` definitions)

Install dependencies:

```sh
pip install grpcio grpcio-tools protobuf
```

---

## Setup

Generate Python gRPC bindings from `geyser.proto` (if not already committed):

```sh
python -m grpc_tools.protoc -I. --python_out=./grpc_gen --grpc_python_out=./grpc_gen geyser.proto
```

Ensure `grpc_gen` is in your `PYTHONPATH` or package accordingly.

---

## Usage

```python
import asyncio
from grpc.aio import insecure_channel
from grpc_gen.geyser_pb2 import CommitmentLevel
from geyser_client import GeyserClient

async def main():
    # Initialize channel and client
    channel = insecure_channel("geyser.solana.com:8124")
    client = GeyserClient(channel, token="YOUR_API_TOKEN")

    # Ping server
    pong = await client.ping(count=3)
    print(f"Ping response: {pong}")

    # Query latest blockhash
    blockhash_info = await client.get_latest_blockhash(CommitmentLevel.FINALIZED)
    print(f"Latest blockhash: {blockhash_info.blockhash}")

    # Subscribe to account updates
    await client.update_subscription(["AccountPubkey1", "AccountPubkey2"])
    async for update in client.responses():
        print("Update received:", update)

    # Close channel when done
    await client.close()

asyncio.run(main())
```

---

## API Reference

### `GeyserClient(channel: Channel, token: str)`

Instantiate the client with an existing gRPC `Channel` and optional API token.

### `async ping(count: int) -> PongResponse`

Send a ping with a specified count. Returns a `PongResponse` containing the count and server timestamp.

### `async get_latest_blockhash(commitment: CommitmentLevel = None) -> GetLatestBlockhashResponse`

Retrieve the most recent blockhash and slot. Optionally specify a `CommitmentLevel`.

### `async get_block_height(commitment: CommitmentLevel = None) -> GetBlockHeightResponse`

Fetch the current block height.

### `async get_slot(commitment: CommitmentLevel = None) -> GetSlotResponse`

Get the current slot number.

### `async is_blockhash_valid(blockhash: str, commitment: CommitmentLevel = None) -> IsBlockhashValidResponse`

Validate a blockhash against the ledger.

### `async get_version() -> GetVersionResponse`

Retrieve the Geyser server version string.

### `async subscribe() -> (Queue[SubscribeRequest], AsyncGenerator[SubscribeUpdate, None])`

Dual queue-generator interface for streaming account updates. Use `update_subscription` to add accounts, and iterate over `responses()` to receive updates.

### `async update_subscription(accounts: List[str])`

Queue a subscription request for the given list of account public keys.

---

## Contributing

Contributions are welcome! Please open issues or pull requests on GitHub. Adhere to PEP8 style and include tests where appropriate.

---

## License

[MIT License](LICENSE)