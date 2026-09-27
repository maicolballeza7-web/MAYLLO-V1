from adaption import Adaption

client = Adaption()
checkpoint = client.autoscientist.download("56437179-6187-4c72-b57b-57f3f8492d2c")

# Métodos típicos de este tipo de respuesta binaria:
if hasattr(checkpoint, "write_to_file"):
    checkpoint.write_to_file("mayllo-best-checkpoint.tgz")
    print("Descargado con write_to_file")
elif hasattr(checkpoint, "content"):
    with open("mayllo-best-checkpoint.tgz", "wb") as f:
        f.write(checkpoint.content)
    print("Descargado con .content")
else:
    print("Métodos disponibles:", dir(checkpoint))
