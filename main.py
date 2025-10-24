"""Ponto de entrada principal para PyInstaller."""

import sys
from pathlib import Path

# Adicionar o diretório pai ao sys.path para resolver imports relativos
# quando executado como script ou por PyInstaller
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Se estiver em um executável PyInstaller, o diretório 'app' estará no _MEIPASS
if hasattr(sys, "_MEIPASS"):
    app_path = Path(sys._MEIPASS) / "app"
    if str(app_path) not in sys.path:
        sys.path.insert(0, str(app_path))
else:
    # Para execução normal, adiciona o diretório 'app'
    app_path = current_dir / "app"
    if str(app_path) not in sys.path:
        sys.path.insert(0, str(app_path))

# Importa e executa a aplicação principal
from app.gui_tk import main  # noqa: E402

if __name__ == "__main__":
    main()
