import asyncio
import signal
import uvicorn
from fastapi import FastAPI
import psutil

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Success! Listening on multiple interfaces."}

class NetworkResolver:
    def resolve(self, expose: list[str], ips:None|str|list[str] = None) -> list[str]:
        if ips is None:
            ips = set()
        elif isinstance(ips, str):
            ips = {ips}
        else:
            ips = set(ips)

        if "local" in expose:
            ips.add("127.0.0.1")

        if "tailscale" in expose:
            for addrs in psutil.net_if_addrs().values():
                for a in addrs:
                    if a.family.name == "AF_INET" and a.address.startswith("100."):
                        ips.add(a.address)
        return list(ips)

class MultiServer:
    def __init__(self, config_list):
        self.servers = [uvicorn.Server(cfg) for cfg in config_list]
        self.should_exit = False

    async def serve(self):
        # 同時啟動所有伺服器實例
        await asyncio.gather(*(s.serve() for s in self.servers))

    def handle_exit(self, sig, frame):
        """處理 Ctrl+C (SIGINT) 訊號"""
        print("\n[System] Gracefully shutting down...")
        for server in self.servers:
            server.should_exit = True

if __name__ == "__main__":
    # 定義你想要監聽的特定 IP 與 Port
    # 請將 '10.8.0.5' 替換為你的 VPN 實際 IP
    resolver = NetworkResolver()
    ips = resolver.resolve(['local','tailscale'])
    configs = [
        uvicorn.Config(app, host=ip, port=8003, log_level="info") for ip in ips
    ]

    manager = MultiServer(configs)

    # 註冊訊號處理器，捕捉 Ctrl+C
    signal.signal(signal.SIGINT, manager.handle_exit)
    signal.signal(signal.SIGTERM, manager.handle_exit)

    # 執行非阻塞的事件迴圈
    asyncio.run(manager.serve())
    f = open("end.txt", 'wb')
