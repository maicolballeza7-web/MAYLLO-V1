import hashlib
from pathlib import Path
import httpx
from adaption import Adaption

client = Adaption()  # lee ADAPTION_API_KEY del entorno

path = Path("mayllo-dataset-final.csv")
data = path.read_bytes()

dataset = client.datasets.create(
    source={
        "name": "MAYLLO Lote Final",
        "file_format": "csv",
        "processing_mode": "raw",
        "column_mapping": {
            "prompt": "prompt",
            "completion": "completion",
        },
    },
)

response = httpx.put(dataset.upload_instructions.url, content=data)
response.raise_for_status()

client.datasets.upload.complete_by_id(
    dataset.dataset_id,
    file_size_bytes=len(data),
    sha256=hashlib.sha256(data).hexdigest(),
)

dataset_id = dataset.dataset_id
print("Dataset:", dataset_id)