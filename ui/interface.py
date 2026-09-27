import os
import threading
import tkinter as tk

import customtkinter as ctk
from PIL import Image, ImageTk

from core.assistant import Assistant
from voice import speak, transcribe_audio


FONDO = "#080C12"
FONDO_TRANSPARENTE = "#010101"
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
IMAGENES = {
    "normal": ["normal.png"],
    "dormido": ["dormido.png"],
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class EstadoMayllo:
    def __init__(self):
        self.estado = "normal"
        self.frame = 0

    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado
        self.frame = 0

    def siguiente_frame(self, cantidad_frames):
        self.frame = (self.frame + 1) % cantidad_frames


def cargar_imagen(nombre):
    ruta = os.path.join(ASSET_DIR, nombre)
    imagen = Image.open(ruta)
    return imagen.resize((220, 190), getattr(Image, "Resampling", Image).LANCZOS)


class MaylloInterface:
    def __init__(self):
        self.estado = EstadoMayllo()
        self.assistant = Assistant()
        self.ventana = tk.Tk()
        self.subtitulo = None
        self.subtitulo_tarjeta = None
        self.subtitulo_label = None
        self.subtitulo_ocultar_id = None
        self.escuchando = False

        self.ventana.overrideredirect(True)
        self.ventana.attributes("-topmost", True)
        self.ventana.config(background=FONDO_TRANSPARENTE)
        self.ventana.wm_attributes("-transparentcolor", FONDO_TRANSPARENTE)

        ancho = self.ventana.winfo_screenwidth()
        alto = self.ventana.winfo_screenheight()
        self.ventana.geometry(f"220x220+{ancho - 250}+{alto - 250}")

        self.canvas = tk.Canvas(
            self.ventana,
            width=220,
            height=220,
            background=FONDO_TRANSPARENTE,
            highlightthickness=0,
        )
        self.canvas.place(x=0, y=0)

        self.imagen_actual = ImageTk.PhotoImage(cargar_imagen(IMAGENES["normal"][0]))
        self.imagen_mayllo = self.canvas.create_image(
            0,
            0,
            image=self.imagen_actual,
            anchor="nw",
        )
        self.sombra = self.canvas.create_oval(
            50,
            190,
            170,
            210,
            fill="#20252A",
            outline="",
        )
        self.canvas.tag_lower(self.sombra)

        self.temporizador = self.ventana.after(10000, self.dormir)
        self.canvas.bind("<Button-1>", self._activar_audio)
        self.canvas.bind("<Button-3>", self.mostrar_menu)

    def animar(self):
        archivo = IMAGENES[self.estado.estado][self.estado.frame]
        self.imagen_actual = ImageTk.PhotoImage(cargar_imagen(archivo))
        self.canvas.itemconfig(self.imagen_mayllo, image=self.imagen_actual)
        self.estado.siguiente_frame(len(IMAGENES[self.estado.estado]))
        self.ventana.after(500, self.animar)

    def cambiar_estado(self, nuevo_estado):
        self.estado.cambiar_estado(nuevo_estado)

    def dormir(self):
        self.cambiar_estado("dormido")

    def _despertar(self):
        self.ventana.after_cancel(self.temporizador)
        if self.estado.estado == "dormido":
            self.cambiar_estado("normal")
        self.temporizador = self.ventana.after(10000, self.dormir)

    def mostrar_menu(self, event):
        menu = tk.Menu(self.ventana, tearoff=0)
        menu.add_command(label="Cerrar MAYLLO", command=self.ventana.destroy)
        menu.post(event.x_root, event.y_root)

    def _activar_audio(self, _event=None):
        self._despertar()
        if self.escuchando:
            return

        self.escuchando = True
        threading.Thread(target=self._procesar_voz, daemon=True).start()

    def _crear_subtitulo(self):
        if self.subtitulo is not None and self.subtitulo.winfo_exists():
            return

        self.subtitulo = tk.Toplevel(self.ventana)
        self.subtitulo.overrideredirect(True)
        self.subtitulo.attributes("-topmost", True)
        self.subtitulo.configure(bg=FONDO_TRANSPARENTE)
        self.subtitulo.wm_attributes("-transparentcolor", FONDO_TRANSPARENTE)

        self.subtitulo_tarjeta = ctk.CTkFrame(
            self.subtitulo,
            corner_radius=18,
            border_width=1,
        )
        self.subtitulo_tarjeta.pack(padx=2, pady=2)
        self.subtitulo_label = ctk.CTkLabel(
            self.subtitulo_tarjeta,
            font=("Segoe UI", 14),
            justify="center",
            wraplength=390,
        )
        self.subtitulo_label.pack(padx=22, pady=12)

    def _mostrar_subtitulo(self, texto, es_usuario, ocultar_despues=None):
        self._crear_subtitulo()
        if self.subtitulo_ocultar_id is not None:
            self.ventana.after_cancel(self.subtitulo_ocultar_id)
            self.subtitulo_ocultar_id = None

        fondo = "#FFFFFF" if es_usuario else "#000000"
        color = "#000000" if es_usuario else "#FFFFFF"
        self.subtitulo_tarjeta.configure(fg_color=fondo, border_color="#2A2A2A")
        self.subtitulo_label.configure(text=texto, text_color=color)

        self.subtitulo.update_idletasks()
        ancho = self.subtitulo.winfo_reqwidth()
        alto = self.subtitulo.winfo_reqheight()
        centro_x = self.ventana.winfo_rootx() + self.ventana.winfo_width() // 2
        posicion_y = self.ventana.winfo_rooty() - alto - 12
        self.subtitulo.geometry(f"{ancho}x{alto}+{centro_x - ancho // 2}+{max(8, posicion_y)}")
        self.subtitulo.deiconify()

        if ocultar_despues is not None:
            self.subtitulo_ocultar_id = self.ventana.after(
                ocultar_despues,
                self._ocultar_subtitulo,
            )

    def _ocultar_subtitulo(self):
        self.subtitulo_ocultar_id = None
        if self.subtitulo is not None and self.subtitulo.winfo_exists():
            self.subtitulo.withdraw()

    def _procesar_voz(self):
        try:
            texto = transcribe_audio()
            if not texto:
                self.ventana.after(0, self._ocultar_subtitulo)
                return

            self.ventana.after(
                0,
                lambda: self._mostrar_subtitulo(texto, es_usuario=True),
            )
            respuesta = self.assistant.respond(texto)
            self.ventana.after(
                0,
                lambda: self._mostrar_subtitulo(
                    respuesta,
                    es_usuario=False,
                    ocultar_despues=5000,
                ),
            )
            threading.Thread(
                target=speak,
                args=(respuesta,),
                daemon=True,
            ).start()
        finally:
            self.ventana.after(0, self._finalizar_escucha)

    def _finalizar_escucha(self):
        self.escuchando = False

    def run(self):
        self.animar()
        self.ventana.mainloop()


InterfazMayllo = MaylloInterface
