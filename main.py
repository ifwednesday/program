"""Ponto de entrada principal para PyInstaller."""

import platform
import sys
from pathlib import Path

# Adicionar o diretório pai ao sys.path para resolver imports relativos
# quando executado como script ou por PyInstaller
current_dir = Path(__file__).resolve().parent
meipass_dir = getattr(sys, "_MEIPASS", None)
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Se estiver em um executável PyInstaller, o diretório 'app' estará no _MEIPASS
if meipass_dir is not None:
    app_path = Path(str(meipass_dir)) / "app"
    if str(app_path) not in sys.path:
        sys.path.insert(0, str(app_path))
else:
    # Para execução normal, adiciona o diretório 'app'
    app_path = current_dir / "app"
    if str(app_path) not in sys.path:
        sys.path.insert(0, str(app_path))


def _validate_runtime() -> int:
    """Valida requisitos mínimos do runtime para evitar crash do Tk no macOS."""
    if meipass_dir is not None:
        # Runtime do executável empacotado usa ambiente controlado do PyInstaller.
        return 0

    if platform.system() != "Darwin":
        return 0

    runtime_paths = {
        Path(sys.executable).resolve().as_posix(),
        Path(sys.prefix).resolve().as_posix(),
        Path(sys.base_prefix).resolve().as_posix(),
    }
    base_executable = getattr(sys, "_base_executable", None)
    if base_executable:
        runtime_paths.add(Path(base_executable).resolve().as_posix())

    if any("/Library/Developer/CommandLineTools/" in p for p in runtime_paths):
        print(
            (
                "Erro de ambiente: este venv usa o Python do Command Line Tools "
                "(Tk 8.5), incompatível "
                "com este app no macOS atual e pode abortar ao abrir a interface.\n"
                "Recrie o venv com Python externo (3.10+) com Tk 8.6."
            ),
            file=sys.stderr,
        )
        return 1

    try:
        import tkinter  # noqa: PLC0415

        if float(tkinter.TkVersion) < 8.6:
            print(
                (
                    f"Erro de ambiente: Tk {tkinter.TkVersion} detectado. "
                    "É necessário Tk 8.6+ para evitar abort no macOS atual."
                ),
                file=sys.stderr,
            )
            return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Erro de ambiente ao validar Tkinter: {exc}", file=sys.stderr)
        return 1

    return 0


def _run() -> int:
    runtime_error = _validate_runtime()
    if runtime_error:
        return runtime_error

    # Importa somente após validar o runtime, para evitar crash no Tk.
    from app.gui_tk import main as app_main  # noqa: E402

    app_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(_run())
