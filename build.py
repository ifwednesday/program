"""Script para build do executável com PyInstaller."""

import shutil
import subprocess
import sys
from pathlib import Path


def clean_build_dirs() -> None:
    """Remove diretórios de build antigos"""
    dirs_to_remove = ["build", "dist"]
    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"Removendo {dir_name}/...")
            shutil.rmtree(dir_path)


def build_executable() -> None:
    """Executa PyInstaller para criar o executável"""
    print("Iniciando build do executável...")

    # Usar python -m pyinstaller para garantir que o módulo correto seja usado

    try:
        subprocess.run(
            [sys.executable, "-m", "PyInstaller", "Qualificador.spec", "--clean"],
            check=True,
        )
        artifact = (
            Path("dist/Qualificador.exe")
            if sys.platform.startswith("win")
            else Path("dist/Qualificador")
        )
        print("\nBuild concluido com sucesso!")
        print(f"Executavel disponivel em: {artifact.absolute()}")
    except subprocess.CalledProcessError as e:
        print(f"\nErro durante o build: {e}")
        raise
    except Exception as e:
        print(f"\nErro ao executar PyInstaller: {e}")
        print("\nVerifique se o PyInstaller está instalado:")
        print("  pip install pyinstaller")
        raise


def main() -> None:
    """Função principal"""
    print("=" * 60)
    print("Build do Qualificador")
    print("=" * 60)

    clean_build_dirs()
    build_executable()


if __name__ == "__main__":
    main()

