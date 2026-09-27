import subprocess
import os

APPS = {
    "spotify": "spotify:",
    "vscode": "code",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "outlook": "outlook",
    "onenote": "onenote",
    "access": "msaccess",
}

OFFICE_PROTOCOLS = {
    "word": "ms-word:ofe|u|",
    "excel": "ms-excel:ofe|u|",
    "powerpoint": "ms-powerpoint:ofe|u|",
    "outlook": "ms-outlook:",
    "onenote": "onenote:",
    "access": "ms-access:",
}

OFFICE_EXECUTABLES = {
    "word": "WINWORD.EXE",
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE",
    "outlook": "OUTLOOK.EXE",
    "onenote": "ONENOTE.EXE",
    "access": "MSACCESS.EXE",
}

OFFICE_DIRECTORIES = (
    os.path.join(
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        "Microsoft Office",
        "root",
        "Office16",
    ),
    os.path.join(
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
        "Microsoft Office",
        "root",
        "Office16",
    ),
)


def _find_office_executable(name: str):
    executable = OFFICE_EXECUTABLES.get(name)
    if not executable:
        return None

    for directory in OFFICE_DIRECTORIES:
        path = os.path.join(directory, executable)
        if os.path.isfile(path):
            return path
    return None


def open_application(name: str):
    name = name.lower()
    comando = APPS.get(name)

    if not comando:
        return {"status": "error", "application": name, "message": "Aplicación no reconocida"}

    try:
        if name in OFFICE_EXECUTABLES:
            executable = _find_office_executable(name)
            if not executable:
                return {
                    "status": "error",
                    "application": name,
                    "message": "No se encontró la aplicación Office instalada",
                }
            subprocess.Popen([executable])
        elif name == "spotify":
            os.system(f"start {comando}")
        else:
            subprocess.Popen(
                ["cmd", "/c", "start", "", comando],
                shell=False,
            )
        return {"status": "ok", "application": name}
    except OSError as error:
        return {"status": "error", "application": name, "message": str(error)}
