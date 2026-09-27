import webbrowser

def open_browser(url: str):
    try:
        webbrowser.open(url)
        return {"status": "ok", "url": url}
    except Exception as e:
        return {"status": "error", "url": url, "message": str(e)}
