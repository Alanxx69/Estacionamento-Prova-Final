from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QAction, QDesktopWidget, QDialog, QHBoxLayout,
    QDateEdit, QHeaderView, QDateTimeEdit, QComboBox, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer, QSize, QDateTime, QTime
from PyQt5.QtGui import QFont, QColor,QIcon
from database.db_manager import Database
from datetime import datetime, timedelta
import traceback

class JanelaBase(QDialog):
    def __init__(self, title, width, height):
        super().__init__()

        # Configurações da janela (diálogo)
        self.setWindowTitle(title)
        self.setGeometry(0, 0, width, height)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.centralizar_janela()

    def centralizar_janela(self):
        # Obter o tamanho da tela
        tela = QDesktopWidget().availableGeometry().center()
        # Obter a geometria da janela
        geometria_janela = self.frameGeometry()

        # Mover a janela para o centro da tela
        geometria_janela.moveCenter(tela)
        self.move(geometria_janela.topLeft())

class JanelaCadastroCliente(JanelaBase):
    def __init__(self, carregar_status_vagas_callback):
        super().__init__("Cadastro de Cliente", 500, 170)
        self.carregar_status_vagas = carregar_status_vagas_callback  # Armazena a função

        # Layout do formulário de cadastro
        cliente_layout = QVBoxLayout()
        self.db = Database()
        cliente_label = QLabel("Cadastrar Cliente")
        self.cpf_input = QLineEdit()
        self.cpf_input.setPlaceholderText("CPF")
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome Completo")

        btn_registrar_cliente = QPushButton("Cadastrar Cliente")
        btn_registrar_cliente.clicked.connect(self.registrar_cliente)
        # Adicionar widgets ao layout
        cliente_layout.addWidget(cliente_label)
        cliente_layout.addWidget(self.cpf_input)
        cliente_layout.addWidget(self.nome_input)
        cliente_layout.addWidget(btn_registrar_cliente)
        self.setLayout(cliente_layout)

    def keyPressEvent(self, event):
        # Se a tecla Enter/Return for pressionada, registra o cliente
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.registrar_cliente()

    def registrar_cliente(self):
        cpf = self.cpf_input.text()
        nome_completo = self.nome_input.text()

        try:
            self.db.registrar_cliente(cpf, nome_completo)
            QMessageBox.information(self, "Sucesso", "Cliente registrado com sucesso!")
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))

class JanelaEntrada(JanelaBase):
    def __init__(self, carregar_status_vagas_callback):
        super().__init__("Entrada", 1200, 608)

        self.carregar_status_vagas = carregar_status_vagas_callback
        self.db = Database()
        self.cliente_id_ = None
        # Aplicar estilo à janela
        # self.setStyleSheet("""
        #     QDialog {
        #         background-color: #F7F9FC;
        #         border-radius: 10px;
        #         border: 1px solid #B0C4DE;
        #     }
        #     QLabel {
        #         font-family: 'Roboto';
        #         font-size: 14px;
        #         color: #1F4E78;
        #         font-weight: bold;
        #     }
        #     QLineEdit {
        #         padding: 10px;
        #         border: 1px solid #B0C4DE;
        #         border-radius: 5px;
        #         background-color: #FFFFFF;
        #         color: #1F4E78;
        #     }
        #     QLineEdit:focus {
        #         border: 2px solid #2C6E91;
        #         background-color: #EDF4FA;
        #     }
        #     QPushButton {
        #         padding: 8px 15px;
        #         border: 2px solid #1F4E78;
        #         border-radius: 5px;
        #         background-color: #1F4E78;
        #         color: #FFFFFF;
        #         font-weight: bold;
        #     }
        #     QPushButton:hover {
        #         background-color: #2C6E91;
        #     }
        #     QPushButton:pressed {
        #         background-color: #153D5C;
        #     }
        #     QComboBox {
        #         padding: 8px;
        #         border: 1px solid #B0C4DE;
        #         border-radius: 5px;
        #         background-color: #FFFFFF;
        #         color: #1F4E78;
        #     }
        #     QComboBox:hover {
        #         border: 1px solid #2C6E91;
        #     }
        #     QTableWidget {
        #         border: 1px solid #A0AEC0;
        #         background-color: #FFFFFF;
        #         gridline-color: #CBD5E0;
        #         color: #2C5282;
        #         alternate-background-color: #E2E8F0;
        #         selection-background-color: #2B6CB0;
        #         selection-color: #FFFFFF;
        #     }
        #     QTableWidget::item:hover {
        #         background-color: #EDF4FA;
        #         color: #1F4E78;
        #     }
        #     QHeaderView::section {
        #         background-color: #EDF4FA;
        #         color: #1F4E78;
        #         padding: 8px;
        #         font-weight: bold;
        #         border: 1px solid #B0C4DE;
        #     }
        # """)
        # Layout Principal
        main_layout = QHBoxLayout(self)

        # Seção Esquerda: Busca de Veículos e Usuários
        left_layout = self._setup_left_section()

        # Seção Direita: Informações do Cliente e Ações
        right_layout = self._setup_right_section()

        # Adicionar layouts ao layout principal
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        # Iniciar Timer para Atualizar Hora
        self._setup_timer()
        self.showMaximized()

    # ----------- Configurações de Layout -----------
    def _setup_left_section(self):
        """Configura a seção esquerda (Busca de veículos e usuários)."""
        left_layout = QVBoxLayout()

        # Grupo: Busca de Veículos
        busca_group = QGroupBox("Busca de Veículos")
        busca_group.setStyleSheet("font-weight: bold; margin: 10px;")
        busca_layout = QVBoxLayout()

        # Campo de CPF e botão de busca
        cpf_layout = QHBoxLayout()
        cpf_label = QLabel("CPF do Cliente:")
        cpf_label.setStyleSheet("font-weight: bold; color: #1F4E78;")
        self.cpf_input = QLineEdit()
        self.cpf_input.setPlaceholderText("Digite o CPF do Cliente")
        btn_buscar = QPushButton("Buscar Veículos")
        btn_buscar.setObjectName("btnBuscar")
        btn_buscar.clicked.connect(self.mostrar_veiculos)

        cpf_layout.addWidget(cpf_label)
        cpf_layout.addWidget(self.cpf_input, 1)
        cpf_layout.addWidget(btn_buscar)
        busca_layout.addLayout(cpf_layout)

        # Seleção de tipo de vaga
        tipo_vaga_layout = QHBoxLayout()
        self.tipo_vaga_label = QLabel("Tipo de Vaga:")
        self.tipo_vaga_label.setStyleSheet("font-weight: bold; color: #1F4E78;")
        self.tipo_vaga_combobox = QComboBox()
        try:
            self.tipo_vaga_combobox.addItems(self.db.get_tipos_vagas())
        except Exception as e:
            print(f"Erro ao carregar tipos de vaga: {str(e)}")
            self.tipo_vaga_combobox.addItems(["Erro ao carregar"])

        self.tipo_vaga_combobox.currentIndexChanged.connect(self.atualizar_vagas_disponiveis)

        tipo_vaga_layout.addWidget(self.tipo_vaga_label)
        tipo_vaga_layout.addWidget(self.tipo_vaga_combobox, 1)
        busca_layout.addLayout(tipo_vaga_layout)

        # Seleção de vaga disponível
        vaga_layout = QHBoxLayout()
        self.vaga_label = QLabel("Vaga Disponível:")
        self.vaga_label.setStyleSheet("font-weight: bold; color: #1F4E78;")
        self.vaga_combobox = QComboBox()
        try:
            self.preencher_vagas_disponiveis()
        except Exception as e:
            print(f"Erro ao carregar vagas disponíveis: {str(e)}")
            self.vaga_combobox.addItems(["Erro ao carregar"])

        vaga_layout.addWidget(self.vaga_label)
        vaga_layout.addWidget(self.vaga_combobox, 1)
        busca_layout.addLayout(vaga_layout)

        busca_group.setLayout(busca_layout)

        # Grupo: Tabela de Veículos
        veiculos_group = QGroupBox("Veículos do Cliente")
        veiculos_group.setStyleSheet("font-weight: bold;")
        veiculos_layout = QVBoxLayout()
        self.veiculos_table = QTableWidget(0, 4)
        self.veiculos_table.setHorizontalHeaderLabels(["ID", "Marca", "Modelo", "Placa"])
        self.veiculos_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.veiculos_table.horizontalHeader().setStretchLastSection(True)
        self.veiculos_table.verticalHeader().setVisible(False)
        veiculos_layout.addWidget(self.veiculos_table)
        veiculos_group.setLayout(veiculos_layout)

        # Grupo: Tabela de Usuários
        usuarios_group = QGroupBox("Usuários Cadastrados")
        usuarios_group.setStyleSheet("font-weight: bold")
        usuarios_layout = QVBoxLayout()

        # Campo de filtro por CPF
        filtro_layout = QHBoxLayout()
        cpf_label_ = QLabel("Filtrar por CPF:")
        cpf_label_.setStyleSheet(" color: #1F4E78;")
        self.cpf_input_user = QLineEdit()
        self.cpf_input_user.setPlaceholderText("Digite o CPF")
        self.cpf_input_user.textChanged.connect(self.filtrar_usuarios)

        filtro_layout.addWidget(cpf_label_)
        filtro_layout.addWidget(self.cpf_input_user)
        usuarios_layout.addLayout(filtro_layout)

        self.usuarios_table = QTableWidget(0, 3)
        self.usuarios_table.setHorizontalHeaderLabels(["ID", "CPF", "Nome"])
        self.usuarios_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.usuarios_table.horizontalHeader().setStretchLastSection(True)
        self.usuarios_table.verticalHeader().setVisible(False)

        usuarios_layout.addWidget(self.usuarios_table)
        usuarios_group.setLayout(usuarios_layout)

        # Adicionar grupos ao layout esquerdo
        left_layout.addWidget(busca_group)
        left_layout.addWidget(veiculos_group)
        left_layout.addWidget(usuarios_group)

        try:
            self.carregar_usuarios()
        except Exception as e:
            print(f"Erro ao carregar usuários: {str(e)}")
            self.usuarios_table.setRowCount(1)
            self.usuarios_table.setItem(0, 0, QTableWidgetItem("Erro ao carregar"))

        return left_layout

    def _setup_right_section(self):
        """Configura a seção direita (Informações do cliente e ações)."""
        right_layout = QVBoxLayout()

        # Grupo: Informações do Cliente
        cliente_group = QGroupBox("Informações do Cliente")
        cliente_group.setStyleSheet("font-weight: bold; margin: 10px;")
        cliente_layout = QVBoxLayout()

        cpf_cliente_label = QLabel("CPF:")
        cpf_cliente_label.setStyleSheet("font-weight: bold; color: #1F4E78;")
        self.cpf_cliente_value = QLineEdit()
        self.cpf_cliente_value.setEnabled(False)

        nome_cliente_label = QLabel("Nome:")
        nome_cliente_label.setStyleSheet("font-weight: bold; color: #1F4E78;")
        self.nome_cliente_value = QLineEdit()
        self.nome_cliente_value.setEnabled(False)

        cliente_layout.addWidget(cpf_cliente_label)
        cliente_layout.addWidget(self.cpf_cliente_value)
        cliente_layout.addWidget(nome_cliente_label)
        cliente_layout.addWidget(self.nome_cliente_value)
        cliente_group.setLayout(cliente_layout)

        # Grupo: Configuração de Tempo
        tempo_group = QGroupBox("Configuração de Tempo")
        tempo_group.setStyleSheet("font-weight: bold; margin: 10px;")
        tempo_layout = QVBoxLayout()

        data_hora_label = QLabel("Data e Hora:")
        data_hora_label.setStyleSheet("font-weight: bold; color: #1F4E78;")
        self.data_hora_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.data_hora_input.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.data_hora_input.setReadOnly(True)

        tempo_estacionamento_label = QLabel("Tempo de Estacionamento:")
        tempo_estacionamento_label.setStyleSheet("font-weight: bold; color: #1F4E78;")
        self.tempo_estacionamento_combobox = QComboBox()
        try:
            tempos_db = self.db.get_precificacao(None, True)
            self.tempo_estacionamento_combobox.addItems(sorted(tempos_db))
        except Exception as e:
            print(f"Erro ao carregar tempos de estacionamento: {str(e)}")
            self.tempo_estacionamento_combobox.addItems(["Erro ao carregar"])

        tempo_layout.addWidget(data_hora_label)
        tempo_layout.addWidget(self.data_hora_input)
        tempo_layout.addWidget(tempo_estacionamento_label)
        tempo_layout.addWidget(self.tempo_estacionamento_combobox)
        tempo_group.setLayout(tempo_layout)

        # Grupo: Ações
        acoes_group = QGroupBox("Ações")
        acoes_group.setStyleSheet("font-weight: bold; margin: 10px;")
        acoes_layout = QVBoxLayout()

        btn_salvar = QPushButton("Salvar Alterações")
        btn_estacionar = QPushButton("Estacionar")
        btn_cadastrar_veiculo = QPushButton("Cadastrar Veículo")

        btn_salvar.clicked.connect(self.salvar_alteracoes_usuario)
        btn_estacionar.clicked.connect(self.registrar_estacionamento)
        btn_cadastrar_veiculo.clicked.connect(self.create_cadastrar_veiculo_section)

        acoes_layout.addWidget(btn_salvar)
        acoes_layout.addWidget(btn_estacionar)
        acoes_layout.addWidget(btn_cadastrar_veiculo)
        acoes_group.setLayout(acoes_layout)

        # Adicionar grupos ao layout direito
        right_layout.addWidget(cliente_group)
        right_layout.addWidget(tempo_group)
        right_layout.addWidget(acoes_group)
        right_layout.addStretch()

        return right_layout

    def _setup_timer(self):
        """Configura o timer para atualizar o relógio."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    # ----------- Funções de Carregamento -----------
    def carregar_usuarios(self):
        """Carrega a lista de usuários cadastrados ao abrir a janela."""
        try:
            usuarios = self.db.get_usuarios()
            self.usuarios_table.setRowCount(0)
            for usuario in usuarios:
                row_position = self.usuarios_table.rowCount()
                self.usuarios_table.insertRow(row_position)
                self.usuarios_table.setItem(row_position, 0, QTableWidgetItem(str(usuario[0])))
                self.usuarios_table.setItem(row_position, 1, QTableWidgetItem(usuario[1]))
                self.usuarios_table.setItem(row_position, 2, QTableWidgetItem(usuario[2]))
        except Exception as e:
            QMessageBox.critical(self, 'Erro', str(e))

    def preencher_vagas_disponiveis(self):
        """Carrega a lista de vagas disponíveis com base no tipo selecionado."""
        try:
            tipo_vaga = self.tipo_vaga_combobox.currentText()
            vagas = self.db.get_vagas_disponiveis(tipo=tipo_vaga)
            self.vaga_combobox.clear()
            for vaga in vagas:
                self.vaga_combobox.addItem(f"{vaga[1]}", vaga[0])
        except Exception as e:
            QMessageBox.critical(self, 'Erro', str(e))

    def atualizar_vagas_disponiveis(self):
        """Atualiza a lista de vagas disponíveis quando o tipo de vaga é alterado."""
        self.preencher_vagas_disponiveis()

    # ----------- Funções de Filtro e Busca -----------
    def filtrar_usuarios(self):
        """Filtra a lista de usuários cadastrados com base no CPF ou nome."""
        filtro = self.cpf_input_user.text().strip()
        for row in range(self.usuarios_table.rowCount()):
            item_cpf = self.usuarios_table.item(row, 1)
            self.usuarios_table.setRowHidden(row, filtro not in item_cpf.text())

    def mostrar_veiculos(self):
        """Mostra os veículos do cliente com base no CPF informado."""
        cpf = self.cpf_input.text().strip()
        try:
            veiculos = self.db.get_veiculo_do_cliente(cpf)
            if not veiculos:
                QMessageBox.warning(self, "Erro", "Nenhum veículo encontrado para este CPF.")
                return

            self.cpf_cliente_value.setText(veiculos[0][1])
            self.nome_cliente_value.setText(veiculos[0][2])
            self.veiculos_table.setRowCount(0)
            for veiculo in veiculos:
                row_position = self.veiculos_table.rowCount()
                self.veiculos_table.insertRow(row_position)
                self.veiculos_table.setItem(row_position, 0, QTableWidgetItem(str(veiculo[0])))
                self.veiculos_table.setItem(row_position, 1, QTableWidgetItem(veiculo[3]))
                self.veiculos_table.setItem(row_position, 2, QTableWidgetItem(veiculo[4]))
                self.veiculos_table.setItem(row_position, 3, QTableWidgetItem(veiculo[5]))
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    # ----------- Funções de Ações -----------
    def salvar_alteracoes_usuario(self):
        """Salva alterações feitas no CPF ou Nome do cliente."""
        cpf = self.cpf_cliente_value.text().strip()
        nome = self.nome_cliente_value.text().strip()
        try:
            self.db.salvar_alteracoes(cpf, nome, self.cliente_id_)
            QMessageBox.information(self, 'Sucesso', 'Alterações salvas com sucesso.')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', str(e))

    def registrar_estacionamento(self):
        """Registra a entrada do veículo selecionado no estacionamento."""
        try:
            vaga_id = self.vaga_combobox.currentData()
            selected_row = self.veiculos_table.currentRow()
            if selected_row == -1 or not vaga_id:
                QMessageBox.warning(self, 'Erro', 'Selecione uma vaga e um veículo.')
                return

            cliente_veiculo_id = self.veiculos_table.item(selected_row, 0).text()
            tempo_estacionamento = self.tempo_estacionamento_combobox.currentText()
            self.db.estacionar(vaga_id, cliente_veiculo_id, tempo_limite=tempo_estacionamento)
            QMessageBox.information(self, 'Sucesso', 'Entrada registrada com sucesso.')
            self.carregar_status_vagas()
            self.preencher_vagas_disponiveis()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', str(e))

    def create_cadastrar_veiculo_section(self):
        """Abre a janela de cadastro de veículos."""
        self.janela_cadastro_veiculo = CadastroVeiculo(self.carregar_status_vagas)
        self.janela_cadastro_veiculo.exec_()

    def update_time(self):
        """Atualiza o widget com a hora atual."""
        self.data_hora_input.setDateTime(QDateTime.currentDateTime())

class CadastroVeiculo(JanelaBase):
    def __init__(self, carregar_status_vagas_callback):
        super().__init__("Cadastro Veiculo", 400, 300)
        self.carregar_status_vagas = carregar_status_vagas_callback

        self.db = Database()
        self.centralizar_janela()

        self.cpf_label = QLabel("CPF do Cliente:")
        self.cpf_input = QLineEdit()

        self.marca_veiculo_label = QLabel("Marca do Veículo:")
        self.marca_veiculo_input = QLineEdit()

        self.modelo_veiculo_label = QLabel("Modelo do Veículo:")
        self.modelo_veiculo_input = QLineEdit()

        self.placa_label = QLabel("Placa do Veículo:")
        self.placa_input = QLineEdit()

        self.cadastrar_button = QPushButton("Cadastrar Veículo")
        self.cadastrar_button.clicked.connect(self.cadastrar_veiculo)

        layout = QVBoxLayout()
        layout.addWidget(self.cpf_label)
        layout.addWidget(self.cpf_input)
        layout.addWidget(self.marca_veiculo_label)
        layout.addWidget(self.marca_veiculo_input)
        layout.addWidget(self.modelo_veiculo_label)
        layout.addWidget(self.modelo_veiculo_input)
        layout.addWidget(self.placa_label)
        layout.addWidget(self.placa_input)
        layout.addWidget(self.cadastrar_button)

        self.setLayout(layout)

    def cadastrar_veiculo(self):
        cpf = self.cpf_input.text().strip()
        marca_veiculo = self.marca_veiculo_input.text().strip()
        modelo_veiculo = self.modelo_veiculo_input.text().strip()
        placa = self.placa_input.text().strip()

        # Validação de CPF: Verificar se é numérico e tem 11 dígitos
        if not cpf or not cpf.isdigit() or len(cpf) != 11:
            QMessageBox.warning(self, "Erro", "CPF inválido. O CPF deve conter exatamente 11 dígitos numéricos.")
            return

        # Verificar se a marca do veículo foi preenchida
        if not marca_veiculo:
            QMessageBox.warning(self, "Erro", "A marca do veículo é obrigatória.")
            return

        # Verificar se o modelo do veículo foi preenchido
        if not modelo_veiculo:
            QMessageBox.warning(self, "Erro", "O modelo do veículo é obrigatório.")
            return

        # Validação da placa: Verificar se a placa tem exatamente 7 caracteres
        if not placa or len(placa) != 7:
            QMessageBox.warning(self, "Erro", "Placa inválida. A placa deve conter exatamente 7 caracteres.")
            return

        try:
            # Registrar o veículo no banco de dados
            self.db.insert_client_veiculo(cpf, marca_veiculo, modelo_veiculo, placa)
            QMessageBox.information(self, "Sucesso", "Veículo cadastrado com sucesso.")
            self.carregar_status_vagas()

        except ValueError as ve:
            QMessageBox.warning(self, "Erro", str(ve))

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao cadastrar o veículo: {str(e)}")

class JanelaSaida(JanelaBase):
    def __init__(self, carregar_status_vagas_callback):
        super().__init__("Saída de Veículos", 1000, 608)
        self.carregar_status_vagas = carregar_status_vagas_callback

        self.db = Database()

        # Layout principal (Horizontal)
        main_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()

        # CPF input e Botão Filtrar Veículos
        cpf_layout = QHBoxLayout()
        cpf_label = QLabel("Filtrar por CPF:")
        self.cpf_input = QLineEdit()
        self.cpf_input.setPlaceholderText("Digite o CPF")
        self.cpf_input.textChanged.connect(self.filtrar_veiculos)

        cpf_layout.addWidget(cpf_label)
        cpf_layout.addWidget(self.cpf_input)

        # Tabela de veículos estacionados
        self.veiculos_table = QTableWidget(0, 5)
        self.veiculos_table.setHorizontalHeaderLabels(["ID", "CPF", "Nome", "Placa", "Vaga"])
        self.veiculos_table.verticalHeader().setVisible(False)

        self.veiculos_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Adicionar CPF layout à esquerda
        left_layout.addLayout(cpf_layout)
        left_layout.addWidget(self.veiculos_table)

        # ---- Seção Direita (Informações do Cliente e Ações) ----
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)

        # Data e Hora
        data_hora_label = QLabel("Data e hora de Saída:")
        self.data_hora_saida_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.data_hora_saida_input.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.data_hora_saida_input.setReadOnly(True)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # Botão de Registrar Saída
        btn_registrar_saida = QPushButton("Registrar Saída")
        btn_registrar_saida.clicked.connect(self.registrar_saida)

        # Adicionar componentes à seção direita
        right_layout.addWidget(data_hora_label)
        right_layout.addWidget(self.data_hora_saida_input)
        right_layout.addWidget(btn_registrar_saida)

        # Adicionar seções ao layout principal
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        # Carregar todos os veículos estacionados
        self.carregar_veiculos_estacionados()

    def carregar_veiculos_estacionados(self):
        """
        Função para carregar todos os veículos que estão estacionados no momento.
        """
        try:
            veiculos_estacionados = self.db.get_veiculos_estacionados()

            self.veiculos_table.setRowCount(0)

            for veiculo in veiculos_estacionados:
                row_position = self.veiculos_table.rowCount()
                self.veiculos_table.insertRow(row_position)
                self.veiculos_table.setItem(row_position, 0, QTableWidgetItem(str(veiculo[0])))
                self.veiculos_table.setItem(row_position, 1, QTableWidgetItem(veiculo[1]))
                self.veiculos_table.setItem(row_position, 2, QTableWidgetItem(veiculo[2]))
                self.veiculos_table.setItem(row_position, 3, QTableWidgetItem(veiculo[3]))
                self.veiculos_table.setItem(row_position, 4, QTableWidgetItem(str(veiculo[4])))

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao carregar os veículos: {str(e)}")

    def filtrar_veiculos(self):
        """
        Função para filtrar os veículos estacionados com base no CPF informado.
        """
        filtro_cpf = self.cpf_input.text().strip()

        for row in range(self.veiculos_table.rowCount()):
            item_cpf = self.veiculos_table.item(row, 1)
            if filtro_cpf in item_cpf.text():
                self.veiculos_table.setRowHidden(row, False)
            else:
                self.veiculos_table.setRowHidden(row, True)

    def update_time(self):
        # Atualiza o widget com a hora atual
        current_time = QDateTime.currentDateTime()
        self.data_hora_saida_input.setDateTime(current_time)

    # Converter tempos para timedelta

    def registrar_saida(self):
        """
        Registra a saída de um veículo selecionado na tabela e calcula o valor final a ser pago,
        considerando o tempo limite e o tempo excedido.
        """
        selected_row = self.veiculos_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Erro', 'Selecione um veículo para registrar a saída.')
            return

        estacionamento_id = self.veiculos_table.item(selected_row, 0).text()

        try:
            # Registrar a saída do veículo no banco de dados
            resultado = self.db.registrar_saida(estacionamento_id, saida=False)
            self.carregar_status_vagas()
            self.carregar_veiculos_estacionados()

            tempo_per, tempo_l = resultado

            # Converter tempos para timedelta
            def str_to_timedelta(time_str):
                try:
                    if "days" in time_str:  # Verificar se o formato inclui dias
                        days, time_part = time_str.split(", ")
                        days = int(days.split()[0])  # Extrair o número de dias
                        hours, minutes, seconds = map(int, time_part.split(":"))
                    else:
                        days = 0
                        hours, minutes, seconds = map(int, time_str.split(":"))
                    return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
                except Exception as e:
                    raise ValueError(f"Erro ao converter tempo: {time_str}. Detalhes: {e}")

            tempo_per_timedelta = str_to_timedelta(tempo_per)
            tempo_l_timedelta = str_to_timedelta(tempo_l)

            # Recuperar o valor inicial associado ao tempo limite
            valor_limite = self.db.get_precificacao(tempo_l, False)[0]

            # Verificar se houve tempo excedido
            if tempo_per_timedelta > tempo_l_timedelta:
                # Calcula o tempo excedido
                delta = tempo_per_timedelta - tempo_l_timedelta

                # Arredondar para cima
                horas_excedidas = delta.total_seconds() // 3600 + (1 if delta.total_seconds() % 3600 > 0 else 0)

                # Calcular valor adicional
                valor_a_mais = int(horas_excedidas) * 10  # 10 reais por hora adicional

                # Calcular valor final
                valor_limite = int(valor_limite)
                valor_final = valor_limite + valor_a_mais
            else:
                valor_final = int(valor_limite)

            # Abrir a nova janela de pagamento
            dados_pagamento = self.db.get_dados_pagamento(estacionamento_id)
            janela_pagamento = JanelaPagamentoDetalhado(
                cliente=dados_pagamento["cliente"],
                veiculo=dados_pagamento["veiculo"],
                vaga=dados_pagamento["vaga"],
                tempo_permanencia=dados_pagamento["tempo_permanencia"],
                tempo_limite=dados_pagamento["tempo_limite"],
                valor_final=dados_pagamento["valor_total"],
                valor_excedente=dados_pagamento["valor_excedente"],
                parent=self
            )
            if janela_pagamento.exec_() == QDialog.Accepted:
                # Se o pagamento foi confirmado, registrar a saída
                resultado = self.db.registrar_saida(estacionamento_id, saida=True)
                self.db.registrar_pagamento(estacionamento_id, valor_final)
                if resultado:
                    pass  # Saída registrada com sucesso
            else:
                pass  # Saída não registrada devido ao cancelamento do pagamento

            # Atualizar a interface
            self.carregar_status_vagas()
            self.carregar_veiculos_estacionados()

        except Exception as e:
            error_message = f"Erro: {str(e)}\n\n{traceback.format_exc()}"
            print(error_message)
            QMessageBox.critical(self, 'Erro', error_message)

class JanelaPagamentoDetalhado(QDialog):
    def __init__(self, cliente, veiculo, vaga, tempo_permanencia, tempo_limite, valor_final, valor_excedente, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sistema de Estacionamento - Pagamento")
        self.setGeometry(300, 200, 500, 600)
        self.setModal(True)

        # Variáveis recebidas
        self.cliente = cliente
        self.veiculo = veiculo
        self.vaga = vaga
        self.tempo_permanencia = tempo_permanencia
        self.tempo_limite = tempo_limite
        self.valor_final = valor_final
        self.valor_excedido = valor_excedente
        self.pagamento_confirmado = False  # Inicialmente, o pagamento não foi confirmado

        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(20)  # Espaçamento entre seções

        # Título com ícone
        titulo_layout = QHBoxLayout()
        titulo_icone = QLabel()
        titulo_icone.setPixmap(QIcon("icons/payment.png").pixmap(32, 32))
        titulo_label = QLabel("Detalhes do Pagamento")
        titulo_label.setFont(QFont('Roboto', 20, QFont.Bold))
        titulo_label.setStyleSheet("color: #1F4E78;")
        titulo_layout.addWidget(titulo_icone)
        titulo_layout.addWidget(titulo_label)
        titulo_layout.addStretch()
        layout.addLayout(titulo_layout)

        # Detalhes do Cliente
        cliente_label = QLabel("👤 Cliente:")
        cliente_label.setFont(QFont('Roboto', 16, QFont.Bold))
        cliente_label.setStyleSheet("color: #1F4E78; margin-bottom: 5px;")

        cliente_info = QLabel(
            f"<b>CPF:</b> {self.cliente['cpf']}<br><b>Nome:</b> {self.cliente['nome']}"
        )
        cliente_info.setFont(QFont('Roboto', 14))
        cliente_info.setStyleSheet("color: #1F4E78;")

        layout.addWidget(cliente_label)
        layout.addWidget(cliente_info)

        # Detalhes do Veículo
        veiculo_label = QLabel("🚗 Veículo:")
        veiculo_label.setFont(QFont('Roboto', 16, QFont.Bold))
        veiculo_label.setStyleSheet("color: #1F4E78; margin-bottom: 5px;")

        veiculo_info = QLabel(
            f"<b>Marca:</b> {self.veiculo['marca']}<br>"
            f"<b>Modelo:</b> {self.veiculo['modelo']}<br>"
            f"<b>Placa:</b> {self.veiculo['placa']}"
        )
        veiculo_info.setFont(QFont('Roboto', 14))
        veiculo_info.setStyleSheet("color: #1F4E78;")

        layout.addWidget(veiculo_label)
        layout.addWidget(veiculo_info)

        # Detalhes da Vaga e Permanência
        vaga_label = QLabel("📍 Vaga e Permanência:")
        vaga_label.setFont(QFont('Roboto', 16, QFont.Bold))
        vaga_label.setStyleSheet("color: #1F4E78; margin-bottom: 5px;")

        vaga_info = QLabel(
            f"<b>Vaga:</b> {self.vaga}<br>"
            f"<b>Tempo de Permanência:</b> {self.tempo_permanencia}<br>"
            f"<b>Tempo Limite:</b> {self.tempo_limite}"
        )
        vaga_info.setFont(QFont('Roboto', 14))
        vaga_info.setStyleSheet("color: #1F4E78;")

        layout.addWidget(vaga_label)
        layout.addWidget(vaga_info)

        # Valor Total
        valor_label = QLabel("💵 Valor a Pagar:")
        valor_label.setFont(QFont('Roboto', 16, QFont.Bold))
        valor_label.setStyleSheet("color: #1F4E78; margin-bottom: 5px;")

        valor_info = QLabel(
            f"<b>Valor Base:</b> R$ {self.valor_final - self.valor_excedido:.2f}<br>"
            f"<b>Valor Excedente:</b> R$ {self.valor_excedido:.2f}<br><hr>"
            f"<b>Valor Total:</b> <b style='color: #E53E3E;'>R$ {self.valor_final:.2f}</b>"
        )
        valor_info.setFont(QFont('Roboto', 14))
        valor_info.setStyleSheet("color: #2C6E91; font-weight: bold;")

        layout.addWidget(valor_label)
        layout.addWidget(valor_info)

        # Botões de Pagamento com ícones
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(15)

        btn_confirmar = QPushButton("Confirmar Pagamento")
        btn_confirmar.setIcon(QIcon("icons/check.png"))
        btn_confirmar.setFont(QFont('Roboto', 14, QFont.Bold))
        btn_confirmar.setStyleSheet("""
            QPushButton {
                background-color: #1F4E78;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #2C6E91;
            }
            QPushButton:pressed {
                background-color: #153D5C;
            }
        """)
        btn_confirmar.clicked.connect(self.confirmar_pagamento)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setIcon(QIcon("icons/cancel.png"))
        btn_cancelar.setFont(QFont('Roboto', 14, QFont.Bold))
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #F7F9FC;
                color: #1F4E78;
                border: 1px solid #B0C4DE;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #EDF4FA;
            }
            QPushButton:pressed {
                background-color: #DCEAF5;
            }
        """)
        btn_cancelar.clicked.connect(self.cancelar_pagamento)

        botoes_layout.addWidget(btn_confirmar)
        botoes_layout.addWidget(btn_cancelar)

        layout.addLayout(botoes_layout)

        # Define o layout principal
        self.setLayout(layout)

    def confirmar_pagamento(self):
        self.pagamento_confirmado = True  # Atualiza a variável para indicar que o pagamento foi confirmado
        QMessageBox.information(
            self,
            "Pagamento",
            "Pagamento confirmado com sucesso!\nObrigado! A transação foi concluída com sucesso."
        )
        self.accept()

    def cancelar_pagamento(self):
        self.pagamento_confirmado = False  # Pagamento não foi confirmado
        QMessageBox.warning(
            self,
            "Pagamento",
            "Pagamento cancelado!\nA transação foi cancelada. Por favor, tente novamente."
        )
        self.reject()

class JanelaConfigurarVagas(JanelaBase):
    def __init__(self, carregar_status_vagas_callback):
        super().__init__("Configurar Vagas", 500, 600)
        self.carregar_status_vagas = carregar_status_vagas_callback
        self.db = Database()

        # Layout principal
        main_layout = QVBoxLayout()

        # Campo para adicionar número da vaga
        self.numero_vaga_input = QLineEdit()
        self.numero_vaga_input.setPlaceholderText("Digite o número da vaga")
        main_layout.addWidget(self.numero_vaga_input)

        # Botão para adicionar vaga
        btn_adicionar_vaga = QPushButton("Adicionar Vaga")
        btn_adicionar_vaga.clicked.connect(self.adicionar_vaga)
        main_layout.addWidget(btn_adicionar_vaga)

        # Tabela para listar vagas existentes
        self.tabela_vagas = QTableWidget(0, 3)
        self.tabela_vagas.setHorizontalHeaderLabels(["Número da Vaga", "Status", "Tipo de Vaga"])
        self.tabela_vagas.verticalHeader().setVisible(False)

        self.tabela_vagas.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.tabela_vagas)

        # Botão para remover vaga selecionada
        btn_remover_vaga = QPushButton("Remover Vaga Selecionada")
        btn_remover_vaga.clicked.connect(self.remover_vaga_selecionada)
        main_layout.addWidget(btn_remover_vaga)

        self.setLayout(main_layout)
        self.carregar_vagas_existentes()

    def carregar_vagas_existentes(self):
        """
        Carrega as vagas existentes e preenche a tabela.
        """
        try:
            vagas = self.db.get_vagas_disponiveis()
            self.tabela_vagas.setRowCount(0)

            for vaga in vagas:
                row_position = self.tabela_vagas.rowCount()
                self.tabela_vagas.insertRow(row_position)
                self.tabela_vagas.setItem(row_position, 0, QTableWidgetItem(str(vaga[0])))
                self.tabela_vagas.setItem(row_position, 1, QTableWidgetItem(vaga[1]))
                self.tabela_vagas.setItem(row_position, 2, QTableWidgetItem(vaga[2]))

        except Exception as e:
            QMessageBox.critical(self, 'Erro', f"Ocorreu um erro ao carregar as vagas: {str(e)}")

    def adicionar_vaga(self):
        """
        Adiciona uma nova vaga ao banco de dados após selecionar o tipo.
        """
        numero_vaga = self.numero_vaga_input.text().strip()

        if not numero_vaga:
            QMessageBox.warning(self, "Erro", "O número da vaga não pode estar vazio.")
            return

        # Exibe a janela de seleção do tipo de vaga
        tipo_vaga = self.selecionar_tipo_vaga()
        if not tipo_vaga:
            QMessageBox.warning(self, "Erro", "Você deve selecionar um tipo de vaga.")
            return

        try:
            # Adicionar a vaga no banco de dados
            self.db.adicionar_vaga(numero_vaga, tipo_vaga)
            QMessageBox.information(self, "Sucesso",
                                    f"A vaga {numero_vaga} do tipo '{tipo_vaga}' foi adicionada com sucesso.")
            self.carregar_vagas_existentes()
            self.carregar_status_vagas()

        except Exception as e:
            QMessageBox.critical(self, 'Erro', f"Erro ao adicionar a vaga: {str(e)}")

    def selecionar_tipo_vaga(self):
        """
        Exibe uma janela para selecionar o tipo de vaga.
        Retorna o tipo selecionado ou None se o usuário cancelar.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecionar Tipo de Vaga")
        dialog.setGeometry(400, 200, 300, 150)

        layout = QVBoxLayout(dialog)

        label = QLabel("Selecione o tipo de vaga:")
        layout.addWidget(label)

        combobox = QComboBox(dialog)
        combobox.addItems(["Carro", "Moto", "Bicicleta", "Caminhão", "Outro"])
        layout.addWidget(combobox)

        button_box = QHBoxLayout()
        ok_button = QPushButton("OK", dialog)
        cancel_button = QPushButton("Cancelar", dialog)
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)

        # Conectar os botões
        def confirmar_selecao():
            dialog.done(1)

        def cancelar():
            dialog.done(0)

        ok_button.clicked.connect(confirmar_selecao)
        cancel_button.clicked.connect(cancelar)

        # Exibir a janela e retornar o tipo selecionado ou None
        if dialog.exec_() == 1:
            return combobox.currentText()
        return None

    def remover_vaga_selecionada(self):
        """
        Remove a vaga selecionada da tabela e do banco de dados.
        """
        selected_row = self.tabela_vagas.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, "Erro", "Selecione uma vaga para remover.")
            return

        numero_vaga = self.tabela_vagas.item(selected_row, 0).text()

        try:
            # Remover a vaga do banco de dados
            self.db.remover_vaga(numero_vaga)
            QMessageBox.information(self, "Sucesso", f"A vaga {numero_vaga} foi removida com sucesso.")
            self.carregar_vagas_existentes()
            self.carregar_status_vagas()

        except Exception as e:
            QMessageBox.critical(self, 'Erro', f"Erro ao remover a vaga: {str(e)}")

class JanelaHistorico(QDialog):
    def __init__(self, db):
        super().__init__()
        self.setWindowTitle("Histórico de Estacionamento")
        self.setGeometry(100, 100, 1000, 600)
        self.db = db

        # Dados carregados
        self.historico_dados = []

        # Layout principal
        layout = QVBoxLayout(self)

        # ---- Filtros ----
        filtro_layout = QHBoxLayout()

        # Filtro por CPF
        self.input_cpf = QLineEdit()
        self.input_cpf.setPlaceholderText("Filtrar por CPF")
        self.input_cpf.textChanged.connect(self.aplicar_filtros)
        filtro_layout.addWidget(self.input_cpf)

        # Filtro por Placa
        self.input_placa = QLineEdit()
        self.input_placa.setPlaceholderText("Filtrar por Placa")
        self.input_placa.textChanged.connect(self.aplicar_filtros)
        filtro_layout.addWidget(self.input_placa)

        # Filtro por Nome
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Filtrar por Nome")
        self.input_nome.textChanged.connect(self.aplicar_filtros)
        filtro_layout.addWidget(self.input_nome)

        layout.addLayout(filtro_layout)

        # ---- Tabela de Histórico ----
        self.table_historico = QTableWidget(0, 11)
        self.table_historico.setHorizontalHeaderLabels(
            ["CPF", "Nome", "Marca", "Modelo", "Placa", "Vaga", "Entrada", "Saída","Tempo Limite", "Tempo permanencia","Valor Pago"]
        )
        self.table_historico.verticalHeader().setVisible(False)
        self.table_historico.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_historico)

        # Carregar o histórico completo inicialmente
        self.carregar_historico()

    def carregar_historico(self):
        """
        Carrega o histórico de entrada e saída de veículos e mantém os dados em memória.
        """
        try:
            self.historico_dados = self.db.get_historico()
            self.table_historico.setRowCount(0)

            for registro in self.historico_dados:
                row_position = self.table_historico.rowCount()
                self.table_historico.insertRow(row_position)
                self.table_historico.setItem(row_position, 0, QTableWidgetItem(str(registro[0])))
                self.table_historico.setItem(row_position, 1, QTableWidgetItem(registro[1]))
                self.table_historico.setItem(row_position, 2, QTableWidgetItem(registro[2]))
                self.table_historico.setItem(row_position, 3, QTableWidgetItem(registro[3]))
                self.table_historico.setItem(row_position, 4, QTableWidgetItem(registro[4]))
                self.table_historico.setItem(row_position, 5, QTableWidgetItem(registro[5]))
                self.table_historico.setItem(row_position, 6, QTableWidgetItem(str(registro[6])))
                self.table_historico.setItem(row_position, 7, QTableWidgetItem(str(registro[7]) if registro[7] else "-"))
                self.table_historico.setItem(row_position, 8, QTableWidgetItem(str(registro[8]) if registro[8] else "-"))
                self.table_historico.setItem(row_position, 9, QTableWidgetItem(str(registro[9]) if registro[9] else "-"))
                self.table_historico.setItem(row_position, 10, QTableWidgetItem(str(registro[11]) if registro[11] else "-"))

        except Exception as e:
            QMessageBox.critical(self, 'Erro', f"Erro ao carregar o histórico: {str(e)}")

    def aplicar_filtros(self):
        """
        Aplica os filtros sobre os dados carregados e atualiza a tabela.
        """
        cpf_filtro = self.input_cpf.text().strip().lower()
        placa_filtro = self.input_placa.text().strip().lower()
        nome_filtro = self.input_nome.text().strip().lower()

        self.table_historico.setRowCount(0)

        for registro in self.historico_dados:
            cpf = str(registro[0]).lower()
            nome = str(registro[1]).lower()
            placa = str(registro[4]).lower()

            if (cpf_filtro in cpf and
                placa_filtro in placa and
                nome_filtro in nome):
                row_position = self.table_historico.rowCount()
                self.table_historico.insertRow(row_position)

                self.table_historico.setItem(row_position, 0, QTableWidgetItem(str(registro[0])))
                self.table_historico.setItem(row_position, 1, QTableWidgetItem(registro[1]))
                self.table_historico.setItem(row_position, 2, QTableWidgetItem(registro[2]))
                self.table_historico.setItem(row_position, 3, QTableWidgetItem(registro[3]))
                self.table_historico.setItem(row_position, 4, QTableWidgetItem(registro[4]))
                self.table_historico.setItem(row_position, 5, QTableWidgetItem(registro[5]))
                self.table_historico.setItem(row_position, 6, QTableWidgetItem(str(registro[6])))
                self.table_historico.setItem(row_position, 7, QTableWidgetItem(str(registro[7]) if registro[7] else "-"))
                self.table_historico.setItem(row_position, 8, QTableWidgetItem(str(registro[8]) if registro[8] else "-"))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configurações da janela principal
        self.setWindowTitle("Sistema de Estacionamento")
        self.setGeometry(380, 130, 1169, 828)
        self.centralizar_janela()

        self.db = Database()

        # Estilização geral
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F7FA;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #CBD5E0;
                border-radius: 5px;
                background-color: #FFFFFF;
                font-size: 14px;
                color: #1A202C;
            }
            QLineEdit:focus {
                border: 2px solid #3182CE;
                background-color: #EDF2F7;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #63B3ED;
            }
            QPushButton:pressed {
                background-color: #2B6CB0;
            }
            QTableWidget {
                border: 1px solid #CBD5E0;
                background-color: #FFFFFF;
                gridline-color: #E2E8F0;
                color: #2D3748;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #EDF2F7;
                color: #2D3748;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #CBD5E0;
            }
        """)

        # Layout principal
        hbox_buttons = QHBoxLayout()

        # Campo de pesquisa de Placa
        self.input_placa = QLineEdit()
        self.input_placa.setPlaceholderText("🔍 Pesquisar Placa")
        self.input_placa.textChanged.connect(self.filtrar_por_placa)
        hbox_buttons.addWidget(self.input_placa)

        # Botões de controle
        self.btn_entrada = QPushButton("ENTRADA")
        self.btn_entrada.clicked.connect(self.create_entrada_section)
        self.btn_saida = QPushButton("SAÍDA")
        self.btn_saida.clicked.connect(self.create_saida_section)
        self.btn_historico = QPushButton("📜 HISTÓRICO")
        self.btn_historico.clicked.connect(self.create_historico_section)

        hbox_buttons.addWidget(self.btn_entrada)
        hbox_buttons.addWidget(self.btn_saida)
        hbox_buttons.addWidget(self.btn_historico)
        hbox_buttons.setAlignment(Qt.AlignTop)
        hbox_buttons.setContentsMargins(10, 10, 10, 10)

        # Criação do container para os botões
        buttons_container = QWidget()
        buttons_container.setLayout(hbox_buttons)

        # Adiciona o container dos botões e a tabela ao layout vertical principal
        vbox_main = QVBoxLayout()
        vbox_main.addWidget(buttons_container)

        # Adicionando Tabela para mostrar status das vagas
        self.vagas_table = QTableWidget(0, 8)  # 8 colunas para exibir as informações
        self.vagas_table.setHorizontalHeaderLabels(
            ["Vaga", "Status", "Tipo de Vaga", "Placa", "Cliente", "Horário de Entrada", "Tempo", "Tempo Limite"]
        )
        header = self.vagas_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.vagas_table.verticalHeader().setVisible(False)

        # Define altura do cabeçalho
        header.setFixedHeight(35)

        vbox_main.addWidget(self.vagas_table)

        # Definindo o layout no container principal da janela
        self.container = QWidget()
        self.container.setLayout(vbox_main)
        self.setCentralWidget(self.container)

        # Timer para atualizar o tempo decorrido
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizar_tempo_decorrido)
        self.timer.start(1000)

        self.carregar_status_vagas()

        # Menu de cadastro de clientes
        menu = self.menuBar()
        menu_cliente = menu.addMenu("Cliente")
        menu_config_vagas = menu.addMenu("Configurar Vagas")

        cadastrar = QAction("Cadastrar", self)
        cadastrar.triggered.connect(self.create_cliente_section)
        menu_cliente.addAction(cadastrar)

        configurar_vagas = QAction("Configurar", self)
        configurar_vagas.triggered.connect(self.create_configuracao_section)
        menu_config_vagas.addAction(configurar_vagas)

    def filtrar_por_placa(self):
        """
        Função para filtrar as vagas com base na placa informada no campo de pesquisa.
        """
        filtro_placa = self.input_placa.text().strip().lower()

        for row in range(self.vagas_table.rowCount()):
            item_placa = self.vagas_table.item(row, 3)
            if filtro_placa in item_placa.text().lower():
                self.vagas_table.setRowHidden(row, False)
            else:
                self.vagas_table.setRowHidden(row, True)

    def centralizar_janela(self):
        tela = QDesktopWidget().availableGeometry().center()
        geometria_janela = self.frameGeometry()
        geometria_janela.moveCenter(tela)
        self.move(geometria_janela.topLeft())

    def carregar_status_vagas(self):
        """
        Função para carregar o status das vagas e exibir na tabela.
        """
        try:
            vagas = self.db.get_status_vagas()
            self.vagas_table.setRowCount(0)

            for vaga in vagas:
                row_position = self.vagas_table.rowCount()
                self.vagas_table.insertRow(row_position)
                self.vagas_table.setItem(row_position, 0, QTableWidgetItem(vaga[0]))
                self.vagas_table.setItem(row_position, 1, QTableWidgetItem(vaga[1]))
                self.vagas_table.setItem(row_position, 2, QTableWidgetItem(vaga[2]))
                self.vagas_table.setItem(row_position, 3, QTableWidgetItem(vaga[3]))
                self.vagas_table.setItem(row_position, 4, QTableWidgetItem(vaga[4]))
                self.vagas_table.setItem(row_position, 5, QTableWidgetItem(vaga[5]))
                self.vagas_table.setItem(row_position, 7, QTableWidgetItem(vaga[6]))
            self.vagas_table.sortItems(0, Qt.AscendingOrder)
            self.atualizar_tempo_decorrido()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f"Ocorreu um erro ao carregar o status das vagas: {str(e)}")

    def atualizar_tempo_decorrido(self):
        """
        Atualiza a coluna de tempo decorrido apenas para as vagas ocupadas.
        """
        try:
            current_time = QDateTime.currentDateTime()

            for row in range(self.vagas_table.rowCount()):
                status_item = self.vagas_table.item(row, 1)
                if status_item.text() == "Ocupada":
                    horario_entrada_item = self.vagas_table.item(row, 5)
                    tempo_limite_td = self.vagas_table.item(row, 7).text()
                    tempo_limite_qtime = QTime.fromString(tempo_limite_td, "HH:mm:ss")
                    tempo_limite_segundos = tempo_limite_qtime.hour() * 3600 + tempo_limite_qtime.minute() * 60 + tempo_limite_qtime.second()

                    if horario_entrada_item:
                        horario_entrada_str = horario_entrada_item.text()
                        horario_entrada = QDateTime.fromString(horario_entrada_str, "dd/MM/yyyy HH:mm:ss")

                        if horario_entrada.isValid():
                            tempo_decorrido = horario_entrada.secsTo(current_time)
                            horas = tempo_decorrido // 3600
                            minutos = (tempo_decorrido % 3600) // 60
                            segundos = tempo_decorrido % 60

                            tempo_formatado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
                            self.vagas_table.setItem(row, 6, QTableWidgetItem(tempo_formatado))

                            try:
                                if tempo_decorrido > tempo_limite_segundos:
                                    for col in range(self.vagas_table.columnCount()):
                                        self.vagas_table.item(row, col).setData(Qt.BackgroundRole, QColor("#FFCCCC"))
                            except ValueError:
                                self.vagas_table.setItem(row, 7, QTableWidgetItem("Limite Inválido"))
                        else:
                            self.vagas_table.setItem(row, 6, QTableWidgetItem("Hora Inválida"))
                    else:
                        self.vagas_table.setItem(row, 5, QTableWidgetItem("Sem Horário"))
                else:
                    self.vagas_table.setItem(row, 6, QTableWidgetItem(""))

        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao atualizar o tempo decorrido: {str(e)}")

    def create_cliente_section(self):
        self.janela_cadastro = JanelaCadastroCliente(self.carregar_status_vagas)
        self.janela_cadastro.exec_()

    def create_entrada_section(self):
        self.janela_entrada = JanelaEntrada(self.carregar_status_vagas)
        self.janela_entrada.exec_()

    def create_saida_section(self):
        self.janela_saida = JanelaSaida(self.carregar_status_vagas)
        self.janela_saida.exec_()

    def create_configuracao_section(self):
        self.janela_configuracao = JanelaConfigurarVagas(self.carregar_status_vagas)
        self.janela_configuracao.exec_()

    def create_historico_section(self):
        self.janela_historico = JanelaHistorico(self.db)
        self.janela_historico.exec_()
