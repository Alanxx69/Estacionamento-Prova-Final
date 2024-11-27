import sys
import traceback
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow


def carregar_estilo_global():
    with open("estilos.qss", "r") as file:
        estilo = file.read()
    return estilo


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        # Carregar o estilo global e aplicar ao QApplication
        app.setStyleSheet(carregar_estilo_global())

        # Agora, todas as janelas carregarão automaticamente o estilo
        janela_principal = MainWindow()
        janela_principal.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Erro na aplicação principal: {e}")
        traceback.print_exc()
