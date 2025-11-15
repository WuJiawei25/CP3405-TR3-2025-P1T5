import asyncio
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"ok": True, "msg": "minimal app"}

async def main():
    config = uvicorn.Config(app, host="127.0.0.1", port=8010, log_level="info")
    server = uvicorn.Server(config)
    print("[debug_start] starting minimal uvicorn on 8010", flush=True)
    task = asyncio.create_task(server.serve())
    await asyncio.sleep(2)
    print("[debug_start] done waiting, server started?", flush=True)
    print("[debug_start] server should be listening on http://127.0.0.1:8010/", flush=True)
    server.should_exit = True
    await task
    print("[debug_start] server exited", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
