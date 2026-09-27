from adaption import Adaption

client = Adaption()

run = client.autoscientist.create(
    dataset_id="6e75855c-7a09-48fe-bd65-f6a403f26b92",
    augmentation_domain_rows=800,
    augmentation_general_rows=530,
)
print("Run:", run.id, "-", run.status)
