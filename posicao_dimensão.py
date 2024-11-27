import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

class MinhaJanela(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configurações da janela
        self.setWindowTitle("Tamanho e Posição em Tempo Real")
        self.setGeometry(100, 100, 400, 300)

    # Função que é chamada quando a janela é redimensionada
    def resizeEvent(self, event):
        tamanho = self.size()
        largura = tamanho.width()
        altura = tamanho.height()

        # Exibir o tamanho no console
        print(f"Largura: {largura}, Altura: {altura}")

        # Garantir que o evento original de redimensionamento seja processado
        super().resizeEvent(event)

    # Função que é chamada quando a janela é movida
    def moveEvent(self, event):
        geometria = self.geometry()
        x = geometria.x()
        y = geometria.y()

        # Exibir a posição no console
        print(f"Posição (x, y): ({x}, {y})")

        # Garantir que o evento original de movimentação seja processado
        super().moveEvent(event)

# Função principal para rodar a aplicação
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = MinhaJanela()
    janela.show()
    sys.exit(app.exec_())
