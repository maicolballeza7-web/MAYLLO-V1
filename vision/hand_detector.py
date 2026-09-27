import cv2
from collections import deque
from math import hypot
import time


CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
PINCH_DISTANCE_THRESHOLD = 40
# Calibrar estos valores con la cámara real mirando la distancia normalizada.
PINCH_CLOSED_THRESHOLD = 0.35
PINCH_OPEN_THRESHOLD = 0.55
PINCH_SMOOTHING_FRAMES = 8
ZOOM_ACTION_COOLDOWN_SECONDS = 0.35
ZOOM_MIN_LEVEL = -5
ZOOM_MAX_LEVEL = 5
PREVIEW_WINDOW_TITLE = "Detector de mano"


FINGER_NAMES = {
    "thumb": "pulgar",
    "index": "índice",
    "middle": "medio",
    "ring": "anular",
    "pinky": "meñique"
}


def get_raised_fingers(hand_landmarks, handedness):
    landmarks = hand_landmarks.landmark
    raised_fingers = []

    # The thumb direction depends on which side of the hand is visible.
    thumb_is_raised = (
        landmarks[4].x < landmarks[3].x
        if handedness == "Right"
        else landmarks[4].x > landmarks[3].x
    )
    if thumb_is_raised:
        raised_fingers.append(FINGER_NAMES["thumb"])

    finger_pairs = (
        ("index", 8, 6),
        ("middle", 12, 10),
        ("ring", 16, 14),
        ("pinky", 20, 18)
    )
    for name, tip_index, pip_index in finger_pairs:
        if landmarks[tip_index].y < landmarks[pip_index].y:
            raised_fingers.append(FINGER_NAMES[name])

    return raised_fingers


def get_thumb_index_distance(hand_landmarks, frame_shape):
    height, width = frame_shape[:2]
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    distance_x = (thumb_tip.x - index_tip.x) * width
    distance_y = (thumb_tip.y - index_tip.y) * height
    return hypot(distance_x, distance_y)


def get_normalized_pinch_distance(hand_landmarks):
    """Devuelve la distancia pulgar-índice relativa al tamaño de la mano."""
    landmarks = hand_landmarks.landmark
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    wrist = landmarks[0]
    middle_base = landmarks[9]

    pinch_distance = hypot(
        thumb_tip.x - index_tip.x,
        thumb_tip.y - index_tip.y,
    )
    hand_size = hypot(
        wrist.x - middle_base.x,
        wrist.y - middle_base.y,
    )
    if hand_size == 0:
        return None
    return pinch_distance / hand_size


class PinchGestureController:
    """Suaviza el pellizco y reporta acciones solo al cambiar de estado."""

    def __init__(
        self,
        closed_threshold=PINCH_CLOSED_THRESHOLD,
        open_threshold=PINCH_OPEN_THRESHOLD,
        smoothing_frames=PINCH_SMOOTHING_FRAMES,
    ):
        if closed_threshold >= open_threshold:
            raise ValueError(
                "closed_threshold debe ser menor que open_threshold."
            )
        if smoothing_frames < 1:
            raise ValueError("smoothing_frames debe ser mayor que cero.")

        self.closed_threshold = closed_threshold
        self.open_threshold = open_threshold
        self._distances = deque(maxlen=smoothing_frames)
        self.state = "neutral"
        self.smoothed_distance = None

    def update(self, hand_landmarks):
        """Procesa un frame y devuelve ``achicar``, ``agrandar`` o ``None``."""
        if hand_landmarks is None:
            self._distances.clear()
            self.smoothed_distance = None
            self.state = "neutral"
            return None

        distance = get_normalized_pinch_distance(hand_landmarks)
        if distance is None:
            return None

        self._distances.append(distance)
        self.smoothed_distance = sum(self._distances) / len(self._distances)

        next_state = self.state
        if self.smoothed_distance <= self.closed_threshold:
            next_state = "cerrado"
        elif self.smoothed_distance >= self.open_threshold:
            next_state = "abierto"

        if next_state == self.state:
            return None

        previous_state = self.state
        self.state = next_state
        if next_state == "cerrado" and previous_state != "cerrado":
            return "achicar"
        if next_state == "abierto" and previous_state != "abierto":
            return "agrandar"
        return None


_last_zoom_action_time = None
_zoom_level = 0


def execute_zoom_action(action):
    """Ejecuta una acción de zoom respetando el foco y el cooldown."""
    global _last_zoom_action_time, _zoom_level

    if action not in {"achicar", "agrandar"}:
        return False

    level_delta = -1 if action == "achicar" else 1
    next_zoom_level = _zoom_level + level_delta
    if not ZOOM_MIN_LEVEL <= next_zoom_level <= ZOOM_MAX_LEVEL:
        print(
            f"Zoom '{action}' ignorado: nivel límite alcanzado "
            f"({_zoom_level}, rango {ZOOM_MIN_LEVEL}..{ZOOM_MAX_LEVEL})."
        )
        return False

    try:
        import pyautogui
    except (ImportError, ModuleNotFoundError) as error:
        raise RuntimeError(
            "El zoom por pellizco requiere PyAutoGUI. "
            "Ejecuta: python -m pip install pyautogui"
        ) from error

    try:
        import win32gui
    except (ImportError, ModuleNotFoundError) as error:
        raise RuntimeError(
            "El diagnóstico y control de foco requiere pywin32. "
            "Ejecuta: python -m pip install pywin32"
        ) from error

    now = time.time()
    if (
        _last_zoom_action_time is not None
        and now - _last_zoom_action_time < ZOOM_ACTION_COOLDOWN_SECONDS
    ):
        print(
            "Zoom ignorado por cooldown "
            f"({ZOOM_ACTION_COOLDOWN_SECONDS * 1000:.0f} ms)."
        )
        return False

    foreground_hwnd = win32gui.GetForegroundWindow()
    foreground_title = win32gui.GetWindowText(foreground_hwnd).strip()
    print(
        f"Zoom '{action}' -> ventana activa: "
        f"'{foreground_title or '(sin título)'}' "
        f"(HWND {foreground_hwnd})"
    )
    if foreground_title == PREVIEW_WINDOW_TITLE:
        # Esto es un problema de foco: la tecla llegó al preview equivocado.
        # Si el título es la app correcta y no cambia el zoom, esa app puede
        # no soportar Ctrl +/-; eso es una limitación de la app destino.
        print(
            "ADVERTENCIA: el preview de OpenCV tiene el foco. "
            "La tecla podría no llegar a la app destino."
        )

    shortcut = "-" if action == "achicar" else "+"
    pyautogui.hotkey("ctrl", shortcut)
    _last_zoom_action_time = now
    _zoom_level = next_zoom_level
    print(f"Nivel de zoom estimado: {_zoom_level}")
    return True


def _configure_preview_window():
    """Muestra el preview sin activar ni robar el foco de otra aplicación."""
    try:
        import win32con
        import win32gui
    except (ImportError, ModuleNotFoundError) as error:
        raise RuntimeError(
            "La ventana de preview requiere pywin32. "
            "Ejecuta: python -m pip install pywin32"
        ) from error

    window_handle = win32gui.FindWindow(None, PREVIEW_WINDOW_TITLE)
    if not window_handle:
        raise RuntimeError("No se encontró la ventana de preview de OpenCV.")

    extended_style = win32gui.GetWindowLong(
        window_handle,
        win32con.GWL_EXSTYLE,
    )
    win32gui.SetWindowLong(
        window_handle,
        win32con.GWL_EXSTYLE,
        extended_style | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOOLWINDOW,
    )


def recognize_gesture(raised_fingers, thumb_index_distance):
    fingers = set(raised_fingers)

    if not fingers:
        return "CLOSE"
    if len(fingers) == 5:
        return "OPEN_MENU"
    if thumb_index_distance <= PINCH_DISTANCE_THRESHOLD:
        return "GRAB"
    if fingers == {"índice"}:
        return "SELECT"
    if fingers == {"índice", "medio"}:
        return "SWITCH_TOOL"
    return "UNKNOWN"


def _load_hand_modules():
    try:
        from mediapipe.python.solutions import drawing_utils, hands
    except (ImportError, ModuleNotFoundError) as error:
        raise RuntimeError(
            "La detección de manos requiere MediaPipe 0.10.21. "
            "Ejecuta: python -m pip install --upgrade "
            "\"mediapipe==0.10.21\""
        ) from error
    return hands, drawing_utils


def main():
    capture = cv2.VideoCapture(CAMERA_INDEX)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not capture.isOpened():
        raise RuntimeError("No se pudo abrir la cámara.")

    hands_module, drawing_module = _load_hand_modules()

    with hands_module.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.4,
        min_tracking_confidence=0.4
    ) as hands:
        pinch_controller = PinchGestureController()
        cv2.namedWindow(
            PREVIEW_WINDOW_TITLE,
            cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL,
        )
        _configure_preview_window()
        try:
            while True:
                success, frame = capture.read()
                if not success:
                    raise RuntimeError("No se pudo leer un frame de la cámara.")

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(frame_rgb)

                raised_fingers_text = "Dedos levantados: ninguno"
                distance_text = "Distancia pulgar-índice: --"
                normalized_distance_text = "Distancia normalizada: --"
                pinch_action_text = "Pellizco: --"
                gesture_text = "Gesto: UNKNOWN"

                if results.multi_hand_landmarks:
                    for hand_index, hand_landmarks in enumerate(
                        results.multi_hand_landmarks
                    ):
                        drawing_module.draw_landmarks(
                            frame,
                            hand_landmarks,
                            hands_module.HAND_CONNECTIONS
                        )

                        handedness = results.multi_handedness[hand_index].classification[0].label
                        raised_fingers = get_raised_fingers(
                            hand_landmarks,
                            handedness
                        )
                        fingers_text = ", ".join(raised_fingers) or "ninguno"
                        raised_fingers_text = (
                            f"Dedos levantados: {fingers_text}"
                        )

                        distance = get_thumb_index_distance(
                            hand_landmarks,
                            frame.shape
                        )
                        distance_text = (
                            f"Distancia pulgar-índice: {distance:.1f} px"
                        )
                        pinch_action = pinch_controller.update(hand_landmarks)
                        normalized_distance = (
                            pinch_controller.smoothed_distance
                        )
                        if normalized_distance is not None:
                            normalized_distance_text = (
                                "Distancia normalizada: "
                                f"{normalized_distance:.3f}"
                            )
                        pinch_action_text = (
                            f"Pellizco: {pinch_controller.state}"
                        )
                        if pinch_action is not None:
                            if execute_zoom_action(pinch_action):
                                pinch_action_text = (
                                    f"Pellizco: {pinch_action}"
                                )
                        gesture_text = (
                            f"Gesto: {recognize_gesture(raised_fingers, distance)}"
                        )
                else:
                    pinch_controller.update(None)

                cv2.putText(
                    frame,
                    raised_fingers_text,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    frame,
                    distance_text,
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    frame,
                    normalized_distance_text,
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 200, 0),
                    2
                )
                cv2.putText(
                    frame,
                    pinch_action_text,
                    (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )
                cv2.putText(
                    frame,
                    gesture_text,
                    (10, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

                cv2.imshow(PREVIEW_WINDOW_TITLE, frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            capture.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
