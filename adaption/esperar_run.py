from adaption import Adaption

client = Adaption()
run_id = "56437179-6187-4c72-b57b-57f3f8492d2c"

print("Esperando a que termine, esto puede tardar...")
run = client.autoscientist.wait_for_completion(run_id)

if run.status != "succeeded":
    print(f"Estado final: {run.status} - {run.error}")
else:
    print(f"Listo. Mejor win rate: {run.best_win_rate}")
