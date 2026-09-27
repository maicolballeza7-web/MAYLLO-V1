import argparse

from core.assistant import Assistant
from ui.interface import MaylloInterface
from voice.voice_controller import process_voice_command

def run_text_mode() -> None:
    assistant = Assistant()
    print("MAYLLO 2.0 listo. Escribe 'salir' para terminar.")
    while True:
        user_input = input("Tú: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"salir", "exit", "quit"}:
            print("MAYLLO: Hasta luego.")
            break
        response = assistant.respond(user_input)
        print(f"MAYLLO: {response}")


def run_ui_mode() -> None:
    interface = MaylloInterface()
    interface.run()


def main() -> None:
    parser = argparse.ArgumentParser(description="MAYLLO 2.0 MVP")
    parser.add_argument("--ui", action="store_true", help="Inicia la interfaz animada de tkinter")
    args = parser.parse_args()

    if args.ui:
        run_ui_mode()
        return

    run_text_mode()


if __name__ == "__main__":
    main()
