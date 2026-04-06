import os
import httpx
from dotenv import load_dotenv

load_dotenv()

PINATA_JWT = os.getenv("PINATA_JWT")

async def upload_json_to_ipfs(json_data: dict) -> str:
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type": "application/json"
    }
    payload = {
        "pinataContent": json_data,
        "pinataMetadata": {
            "name": f"PillProof_Batch_{json_data.get('batch_number', 'unknown')}"
        }
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result["IpfsHash"]
        else:
            print(f"Pinata Error: {response.text}")
            return None
