import asyncio
import httpx
import time

API_URL = "https://192.168.0.120:8443/execute"
HEADERS = {"api-key": "tu_clave_secreta_aqui"}

payload_docker = {
    "server": "SQL2025_DOCKER",
    "database": "ERP_DB",
    "operation": "consultaAPI",
    "procedure": "SELECT @@VERSION as version",
    "parameters": {}
}

async def send_request(client, i):
    start = time.perf_counter()
    try:
        # verify=False porque usamos certificados autofirmados
        response = await client.post(API_URL, json=payload_docker, timeout=10)
        end = time.perf_counter()
        print(f"Req {i}: Status {response.status_code} - Tiempo: {end - start:.2f}s")
    except Exception as e:
        print(f"Req {i}: Falló - {e}")

async def main():
    # Límitamos a 50 conexiones simultáneas
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=50)
    async with httpx.AsyncClient(headers=HEADERS, verify=False, limits=limits) as client:
        tasks = [send_request(client, i) for i in range(50)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())