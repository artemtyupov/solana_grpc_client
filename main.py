import asyncio
from dataclasses import dataclass
from typing import AsyncGenerator, Optional, Tuple

import grpc
from grpc.aio._channel import Channel
from grpc_gen import geyser_pb2, geyser_pb2_grpc
from grpc_gen.geyser_pb2 import CommitmentLevel

class GeyserClient:
    def __init__(self, channel: Channel, token):
        self._channel = channel
        self.geyser = geyser_pb2_grpc.GeyserStub(channel)
        if token != "":
            self.metadata = (('x-token', token),)
        else:
            self.metadata = ()
        self.queue_responses = asyncio.Queue()
        self._outgoing_requests = asyncio.Queue()

    async def close(self):
        await self._channel.close()

    async def responses(self):
        while True:
            data = await self.queue_responses.get()
            yield data

    async def update_subscription(self, accounts: list[str]):
        req = geyser_pb2.SubscribeRequest()
        req.accounts['raydium'].account.extend(accounts)
        req.commitment = geyser_pb2.CommitmentLevel.PROCESSED
        await self._outgoing_requests.put(req)

    async def subscribe(
        self,
    ) -> Tuple[
        asyncio.Queue[geyser_pb2.SubscribeRequest],
        AsyncGenerator[geyser_pb2.SubscribeUpdate, None],
    ]:

        async def request_iterator() -> AsyncGenerator[geyser_pb2.SubscribeRequest, None]:
            while True:
                req = await self._outgoing_requests.get()
                yield req
        while True:
            call = self.geyser.Subscribe(request_iterator(), compression=grpc.Compression.NoCompression)
            try:
                async for response in call:
                    await self.queue_responses.put(response)
            except Exception as e:
                print(f"-" * 100)
                print(f"grpc error: {e}")
                print(f"-" * 100)
                raise e

    async def ping(self, count: int) -> geyser_pb2.PongResponse:
        request = geyser_pb2.PingRequest(count=count)
        return await self.geyser.Ping(request)

    async def get_latest_blockhash(
        self, commitment: Optional[CommitmentLevel] = None
    ) -> geyser_pb2.GetLatestBlockhashResponse:
        request = geyser_pb2.GetLatestBlockhashRequest()
        if commitment is not None:
            request.commitment = commitment.value
        proto_response = await self.geyser.GetLatestBlockhash(request)
        return geyser_pb2.GetLatestBlockhashResponse(
            slot=proto_response.slot,
            blockhash=proto_response.blockhash,
            last_valid_block_height=proto_response.last_valid_block_height,
        )

    async def get_block_height(
        self, commitment: Optional[CommitmentLevel] = None
    ) -> geyser_pb2.GetBlockHeightResponse:
        request = geyser_pb2.GetBlockHeightRequest()
        if commitment is not None:
            request.commitment = commitment.value
        proto_response = await self.geyser.GetBlockHeight(request)
        return geyser_pb2.GetBlockHeightResponse(
            block_height=proto_response.block_height
        )

    async def get_slot(
        self, commitment: Optional[CommitmentLevel] = None
    ) -> geyser_pb2.GetSlotResponse:
        request = geyser_pb2.GetSlotRequest()
        if commitment is not None:
            request.commitment = commitment.value
        proto_response = await self.geyser.GetSlot(request)
        return geyser_pb2.GetSlotResponse(slot=proto_response.slot)

    async def is_blockhash_valid(
        self, blockhash: str, commitment: Optional[CommitmentLevel] = None
    ) -> geyser_pb2.IsBlockhashValidResponse:
        request = geyser_pb2.IsBlockhashValidRequest(blockhash=blockhash)
        if commitment is not None:
            request.commitment = commitment.value
        proto_response = await self.geyser.IsBlockhashValid(request)
        return geyser_pb2.IsBlockhashValidResponse(
            slot=proto_response.slot,
            valid=proto_response.valid,
        )

    async def get_version(self) -> geyser_pb2.GetVersionResponse:
        request = geyser_pb2.GetVersionRequest()
        proto_response = self.geyser.GetVersion(request)
        return geyser_pb2.GetVersionResponse(version=proto_response.version)