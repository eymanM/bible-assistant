import asyncio
import queue
import threading

async def demo_gen():
    yield "event: results\ndata: {}\n\n"
    await asyncio.sleep(0.5)
    yield "event: token\ndata: {}\n\n"

def sync_bridge(async_func, *args, **kwargs):
    q = queue.Queue()

    def run_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async def consume():
                try:
                    agen = async_func(*args, **kwargs)
                    async for item in agen:
                        q.put(item)
                except Exception as e:
                    q.put(("error", str(e)))
            loop.run_until_complete(consume())
        finally:
            q.put(("done", None))
            loop.close()

    t = threading.Thread(target=run_loop)
    t.start()

    while True:
        item = q.get()
        if isinstance(item, tuple) and len(item) == 2:
            typ, val = item
            if typ == "error":
                raise RuntimeError(val)
            elif typ == "done":
                break
        else:
            yield item

if __name__ == '__main__':
    for item in sync_bridge(demo_gen):
        print("Got:", item.strip())
