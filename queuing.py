import asyncio
import time
from typing import Awaitable, Callable
from utils import Persistable, PersistedList
import logging

logger = logging.getLogger(__name__)


class QueueManager:
    def __init__(
        self,
        send_message_callback: Callable[[int, str], Awaitable],
        kick_time_seconds=60 * 60 * 4,
        max_queue_size=24,
    ):
        self.serving_list = PersistedList("data/serving_list.json")
        self.waiting_list = PersistedList("data/waiting_list.json")
        self.kick_time_seconds = kick_time_seconds
        self.max_queue_size = max_queue_size
        self.send_message_callback = send_message_callback

        self.last_kick_time = Persistable("data/last_kick_time")

    def quit_queue(self, chat_id):
        if chat_id in self.serving_list.items:
            self.serving_list.remove(chat_id)
        if chat_id in self.waiting_list.items:
            self.waiting_list.remove(chat_id)

    def try_kick(self):
        """Returns True if someone was kicked, False otherwise."""
        if len(self.waiting_list.items) > 0 and (
            self.last_kick_time.data is None
            or time.time() - self.last_kick_time.data > self.kick_time_seconds
        ):
            kicked_one = self.serving_list.pop()
            self.serving_list.append(self.waiting_list.pop())
            self.last_kick_time.data = time.time()
            self.last_kick_time.save()
            return kicked_one
        return False

    async def join_queue(self, chat_id):
        # Already in a queue:
        if chat_id in self.serving_list.items:
            await self.send_message_callback(chat_id, "You are already subscribed.")
            return
        if chat_id in self.waiting_list.items:
            await self.send_message_callback(
                chat_id,
                f"You are {self.waiting_list.items.index(chat_id)} in the queue.",
            )
            return

        # Main queue has capacity:
        if len(self.serving_list.items) < self.max_queue_size:
            self.serving_list.append(chat_id)
            await self.notify_serving()
            return

        # If the queue is full:
        self.waiting_list.append(chat_id)
        await self.send_message_callback(
            chat_id,
            f"You are {self.waiting_list.items.index(chat_id)} in the queue.",
        )

    async def notify_queue_position(self):
        for i, chat_id in enumerate(self.waiting_list.items):
            await self.send_message_callback(chat_id, f"You are {i} in the queue.")

    async def notify_serving(self):
        chat_id = self.serving_list.items[-1]
        await self.send_message_callback(chat_id, "You are now subscribed.")

    async def process_queue(self):
        kicked_one = self.try_kick()
        if kicked_one:
            await self.send_message_callback(
                kicked_one, "You have been kicked due to inactivity."
            )
            await self.notify_queue_position()
            await self.notify_serving()

        await asyncio.sleep(1)
        asyncio.create_task(self.process_queue())
