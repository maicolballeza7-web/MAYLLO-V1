from adaption import Adaption

client = Adaption()
dataset_id = "6e75855c-7a09-48fe-bd65-f6a403f26b92"

domain_rows_to_add = 800   # arranque conservador, no 20,000
general_rows_to_add = 530  # ~40% del total, para no perder capacidad general

run = client.autoscientist.create(
    dataset_id=dataset_id,
    augmentation_domain_rows=domain_rows_to_add,
    augmentation_general_rows=general_rows_to_add,
)
print("Run:", run.id, "-", run.status)
