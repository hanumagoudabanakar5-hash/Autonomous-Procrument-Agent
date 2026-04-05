import subprocess
import os
from pathlib import Path

contracts = ["MediRegistry", "ProcurementEscrow", "CounterfeitAlert"]
output_dir = Path("artifacts")
output_dir.mkdir(exist_ok=True)

for contract in contracts:
    print(f"-> Compiling {contract}...")
    # This command forces the output into the 'artifacts' folder
    result = subprocess.run(
        ["puyapy", f"{contract}.py", "--out-dir", str(output_dir)],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Error compiling {contract}: {result.stderr}")
        continue

    # Look for the ARC-32 JSON file
    json_path = output_dir / f"{contract}.arc32.json"
    if json_path.exists():
        print(f"✅ Generated: {json_path}")
        # TRIGGER DEPLOYMENT LOGIC HERE using json_path
    else:
        print(f"❌ JSON not found at {json_path}")