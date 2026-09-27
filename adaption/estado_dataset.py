import time
from adaption import Adaption

client = Adaption()
dataset_id = "6e75855c-7a09-48fe-bd65-f6a403f26b92"

while True:
    status = client.datasets.get_status(dataset_id)
    if status.status == "failed":
        err = status.error_data
        print("Error:", err.message if err else "unknown")
        break
    if status.row_count is not None:
        print(f"Importadas {status.row_count} filas")
        break
    time.sleep(5)
