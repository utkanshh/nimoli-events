import os
import socket
import sys
import threading
import tkinter as tk
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from tkinter import messagebox
from wsgiref.simple_server import WSGIRequestHandler, make_server


class QuietRequestHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        return


def application_root():
    if getattr(sys, "frozen", False):
        candidates = [
            Path(sys._MEIPASS),
            Path(sys.executable).parent,
            Path(sys.executable).parent / "_internal",
            Path(sys.executable).parent.parent / "Resources",
        ]
        for candidate in candidates:
            if (candidate / "gather_rsvp" / "settings.py").is_file():
                return candidate
        raise RuntimeError("The bundled Nimoli Bhandari Events files could not be found.")
    return Path(__file__).resolve().parent


def data_root():
    return user_data_directory(
        system=sys.platform,
        environ=os.environ,
        home=Path.home(),
    )


def user_data_directory(system, environ, home):
    if system == "darwin":
        path = home / "Library" / "Application Support" / "Gather RSVP"
    elif system == "win32":
        path = Path(environ.get("LOCALAPPDATA", str(home / "AppData" / "Local")))
        path = path / "Gather RSVP"
    else:
        data_home = Path(
            environ.get("XDG_DATA_HOME", str(home / ".local" / "share"))
        )
        path = data_home / "gather-rsvp"
    path.mkdir(parents=True, exist_ok=True)
    return path


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def main():
    root_path = application_root()
    os.chdir(root_path)
    sys.path.insert(0, str(root_path))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gather_rsvp.settings")
    os.environ["DJANGO_DEBUG"] = "true"
    os.environ["DJANGO_LOCAL_DEMO_MODE"] = "true"
    os.environ.pop("DATABASE_URL", None)
    os.environ["GATHER_DATABASE_PATH"] = str(data_root() / "gather.sqlite3")
    os.environ["GATHER_MEDIA_ROOT"] = str(data_root() / "media")

    import django
    from django.core.management import call_command
    from django.core.wsgi import get_wsgi_application
    from django.contrib.staticfiles.handlers import StaticFilesHandler

    django.setup()
    call_command("migrate", interactive=False, verbosity=0)
    sample_cleanup_marker = data_root() / "demo-samples-removed-v1"
    if not sample_cleanup_marker.exists():
        call_command("remove_demo", verbosity=0)
        sample_cleanup_marker.write_text("done\n", encoding="ascii")

    port = free_port()
    (data_root() / "server-port.txt").write_text(str(port), encoding="ascii")
    server = None
    server_thread = None
    window = tk.Tk()
    window.title("Nimoli Bhandari Events")
    window.geometry("420x250")
    window.resizable(False, False)
    window.configure(bg="#f7f8f5")

    def shutdown():
        nonlocal server
        if server is not None:
            server.shutdown()
            server.server_close()
            server = None
        window.destroy()

    def open_dashboard():
        webbrowser.open(f"http://127.0.0.1:{port}/")

    try:
        app = StaticFilesHandler(get_wsgi_application())
        server = make_server(
            "127.0.0.1",
            port,
            app,
            handler_class=QuietRequestHandler,
        )
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=10):
            pass
    except (OSError, urllib.error.URLError) as exc:
        if server is not None:
            server.server_close()
        messagebox.showerror(
            "Could not start Nimoli Bhandari Events",
            f"The local RSVP app could not start.\n\n{exc}",
        )
        return

    tk.Label(
        window,
        text="Nimoli Bhandari Events",
        font=("Georgia", 27),
        fg="#18332c",
        bg="#f7f8f5",
    ).pack(pady=(25, 5))
    tk.Label(
        window,
        text="Your event dashboard is running on this computer.",
        font=("Arial", 10),
        fg="#74837d",
        bg="#f7f8f5",
    ).pack(pady=(0, 17))
    tk.Button(
        window,
        text="Open RSVP dashboard",
        command=open_dashboard,
        font=("Arial", 10, "bold"),
        bg="#24735a",
        fg="white",
        activebackground="#195641",
        activeforeground="white",
        relief="flat",
        padx=18,
        pady=10,
    ).pack()
    tk.Label(
        window,
        text="Your data stays on this computer. This desktop app does not\nsend WhatsApp messages or sync with phones.",
        font=("Arial", 9),
        fg="#74837d",
        bg="#f7f8f5",
        justify="center",
    ).pack(pady=15)
    tk.Button(
        window,
        text="Exit Nimoli Bhandari Events",
        command=shutdown,
        font=("Arial", 9),
        bg="#ffffff",
        fg="#18332c",
        relief="solid",
        bd=1,
        padx=13,
        pady=6,
    ).pack()
    window.protocol("WM_DELETE_WINDOW", shutdown)
    window.mainloop()
    if server_thread and server_thread.is_alive():
        server_thread.join(timeout=3)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ImportError) as exc:
        try:
            messagebox.showerror(
                "Nimoli Bhandari Events could not start",
                f"{exc}\n\nNo guest data was sent.",
            )
        except tk.TclError:
            raise
