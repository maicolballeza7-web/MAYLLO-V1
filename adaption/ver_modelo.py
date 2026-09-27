from adaption import Adaption

client = Adaption()
run = client.autoscientist.get("4108e066-1597-47fd-a585-c72c0a69a4fd")

print("Estado:", run.status)
print("Modelo base:", getattr(run, "original_model_name", None) or getattr(run, "model", None))
print(run)
