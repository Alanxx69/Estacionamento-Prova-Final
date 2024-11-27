from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QMessageBox, QAction, QDesktopWidget, QDialog, QHBoxLayout, QDateEdit,QHeaderView,QDateTimeEdit,QComboBox)
from PyQt5.QtCore import Qt, QTimer,QSize,QDateTime
from PyQt5.QtGui import QFont
from database.db_manager import Database
import datetime

class JanelaBase(QDialog):
    def __init__(self, title, width, height):
        super().__init__()

        # Configurações da janela (diálogo)
        self.setWindowTitle(title)
        self.setGeometry(0, 0, width, height)
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
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
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
        self.carregar_status_vagas = carregar_status_vagas_callback  # Armazena a função

        self.db = Database()
        # Layout principal (Vertical)
        main_layout = QHBoxLayout(self)
        self.cliente_id_ = None
        left_layout = QVBoxLayout()
        # CPF input e Botão Buscar Veículos
        cpf_layout = QHBoxLayout()
        cpf_label = QLabel("CPF:")
        self.cpf_input = QLineEdit()
        self.cpf_input.setPlaceholderText("Digite o CPF do Cliente")
        btn_buscar = QPushButton("Buscar veículos")
        btn_buscar.setObjectName("btnBuscar")

        btn_buscar.clicked.connect(self.mostrar_veiculos)

        # Tabela de veículos
        self.veiculos_table = QTableWidget(0, 4)
        self.veiculos_table.setHorizontalHeaderLabels(["id","Marca", "Modelo", "Placa"])
        self.veiculos_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.veiculos_table.verticalHeader().setVisible(False)
        self.veiculos_table.setColumnWidth(0, 5)

        self.vaga_label = QLabel('Selecione a Vaga:')
        cpf_layout.addWidget(self.vaga_label)
        self.vaga_combobox = QComboBox()
        self.vaga_combobox.setStyleSheet("padding: 5px;")
        cpf_layout.addWidget(self.vaga_combobox)
        self.preencher_vagas_disponiveis()

        # Adicionar elementos à seção esquerda
        left_layout.addLayout(cpf_layout)
        left_layout.addWidget(self.veiculos_table)

        cpf_layout.addWidget(cpf_label)
        cpf_layout.addWidget(self.cpf_input)
        cpf_layout.addWidget(btn_buscar)

        buscar_usuario_layout = QHBoxLayout()


        # cpf_layout = QHBoxLayout()
        cpf_label_ = QLabel("Filtrar por CPF:")
        self.cpf_input_user = QLineEdit()
        self.cpf_input_user.setPlaceholderText("Digite o CPF")
        self.cpf_input_user.textChanged.connect(self.filtrar_usuarios)  # Filtro instantâneo

        buscar_usuario_layout.addWidget(cpf_label_)
        buscar_usuario_layout.addWidget(self.cpf_input_user)


        # Tabela de usuários cadastrados
        self.usuarios_table = QTableWidget(0, 3)  # 3 colunas: id, CPF, Nome
        self.usuarios_table.setHorizontalHeaderLabels(["id", "CPF", "Nome"])
        self.usuarios_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.usuarios_table.verticalHeader().setVisible(False)
        self.usuarios_table.setColumnWidth(0, 5)
        self.carregar_usuarios()

        # Adicionar campo de busca e tabela de usuários ao layout esquerdo
        left_layout.addLayout(buscar_usuario_layout)
        left_layout.addWidget(self.usuarios_table)

        # ---- Seção Direita (Informações do Cliente e Ações) ----
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)

        # Dados do cliente
        cliente_label = QLabel("Dados Cliente")
        # cliente_label.setFont(QFont("Arial", 12, QFont.Bold))

        cpf_cliente_label = QLabel("CPF:")
        self.cpf_cliente_value = QLineEdit()
        self.cpf_cliente_value.setEnabled(False)  # Desativa o input
        # Será preenchido dinamicamente
        nome_cliente_label = QLabel("Nome:")
        self.nome_cliente_value = QLineEdit()
        self.nome_cliente_value.setEnabled(False)  # Desativa o input
        # Será preenchido dinamicamente

        # Botão Salvar Alterações
        btn_salvar = QPushButton("Salvar Alterações")
        btn_salvar.clicked.connect(self.salvar_alteracoes_usuario)

        # Data e Hora
        data_hora_label = QLabel("Data e hora:")
        self.data_hora_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.data_hora_input.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        self.data_hora_input.setReadOnly(True)  # Somente leitura, será preenchido automaticamente
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # Botões de Estacionar e Cadastrar Veículo
        btn_estacionar = QPushButton("Estacionar")
        btn_estacionar.clicked.connect(self.registrar_estacionamento)

        btn_cadastrar_veiculo = QPushButton("Cadastrar Veículo")
        btn_cadastrar_veiculo.clicked.connect(self.create_cadastrar_veiculo_section)

        # Adicionar elementos à seção direita
        right_layout.addWidget(cliente_label)
        right_layout.addWidget(cpf_cliente_label)
        right_layout.addWidget(self.cpf_cliente_value)
        right_layout.addWidget(nome_cliente_label)
        right_layout.addWidget(self.nome_cliente_value)
        right_layout.addWidget(btn_salvar)
        right_layout.addWidget(data_hora_label)
        right_layout.addWidget(self.data_hora_input)
        right_layout.addWidget(btn_estacionar)
        right_layout.addWidget(btn_cadastrar_veiculo)

        # Adicionar seções ao layout principal
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
    def carregar_usuarios(self):
        """
        Carrega a lista de usuários cadastrados ao abrir a janela.
        """
        try:
            # Buscar todos os usuários no banco
            usuarios = self.db.get_usuarios()
            self.usuarios_table.setRowCount(0)  # Limpar tabela

            # Preencher a tabela de usuários
            for usuario in usuarios:
                row_position = self.usuarios_table.rowCount()
                self.usuarios_table.insertRow(row_position)
                self.usuarios_table.setItem(row_position, 0, QTableWidgetItem(str(usuario[0])))  # id
                self.usuarios_table.setItem(row_position, 1, QTableWidgetItem(usuario[1]))  # CPF
                self.usuarios_table.setItem(row_position, 2, QTableWidgetItem(usuario[2]))  # Nome

        except Exception as e:
            QMessageBox.critical(self, 'Erro', str(e))
    def filtrar_usuarios(self):
        """
        Filtra a lista de usuários cadastrados com base no CPF ou nome.
        """
        filtro = self.cpf_input_user.text().strip()

        for row in range(self.usuarios_table.rowCount()):
            item_cpf = self.usuarios_table.item(row, 1)  # CPF está na segunda coluna (indice 1)
            if filtro in item_cpf.text():
                self.usuarios_table.setRowHidden(row, False)  # Mostra a linha se corresponder ao filtro
            else:
                self.usuarios_table.setRowHidden(row, True)  # Oculta a linha se não corresponder ao filtro

    def create_cadastrar_veiculo_section(self):
        # Criar e exibir a nova janela de cadastro
        self.janela_cadastro_veiculo = CadastroVeiculo(self.carregar_status_vagas)
        self.janela_cadastro_veiculo.exec_()
    def mostrar_veiculos(self):
        # Recupera o CPF do campo de entrada
        cpf = self.cpf_input.text().strip()
        try:
            # Busca os veículos do cliente no banco
            veiculos = self.db.get_veiculo_do_cliente(cpf)
            self.cliente_id_ = veiculos[0][6]
            # Verifique se a lista de veículos está vazia
            if not veiculos:
                QMessageBox.warning(self, "Erro", "Nenhum veículo encontrado para este CPF.")
                return

            # Acessa o primeiro veículo na lista e verifica se há dados
            # Verifique se veiculos[2] existe antes de tentar acessá-lo
            # Preenche os campos de CPF e Nome
            self.cpf_cliente_value.setText(veiculos[0][1])
            self.cpf_cliente_value.setEnabled(True)# Preenche o CPF do cliente (indice 1)
            self.nome_cliente_value.setText(veiculos[0][2])
            self.nome_cliente_value.setEnabled(True)# Preenche o nome do cliente (indice 2)

            # Limpa a tabela antes de mostrar novos dados
            self.veiculos_table.setRowCount(0)

            # Preenche a tabela com os dados retornados
            for veiculo in veiculos:
                row_position = self.veiculos_table.rowCount()
                self.veiculos_table.insertRow(row_position)
                self.veiculos_table.setItem(row_position, 0, QTableWidgetItem(str(veiculo[0])))  # id (indice 0)
                self.veiculos_table.setItem(row_position, 1, QTableWidgetItem(veiculo[3]))  # Marca (indice 3)
                self.veiculos_table.setItem(row_position, 2, QTableWidgetItem(veiculo[4]))  # Modelo (indice 4)
                self.veiculos_table.setItem(row_position, 3, QTableWidgetItem(veiculo[5]))  # Placa (indice 5)
                # Placa (indice 5)

        except ValueError as e:
            # Exibe uma mensagem de erro caso ocorra algum problema
            QMessageBox.warning(self, "Erro", str(e))

        except Exception as e:
            # Lida com exceções inesperadas
            QMessageBox.critical(self, "Erro inesperado", f"Ocorreu um erro: {str(e)}")

    def preencher_vagas_disponiveis(self):
        try:
            vagas = self.db.get_vagas_disponiveis()
            self.vaga_combobox.clear()
            for vaga in vagas:
                self.vaga_combobox.addItem(f"{vaga[0]}", vaga[0])
        except Exception as e:
            QMessageBox.critical(self, 'Erro', str(e))

    def update_time(self):
        # Atualiza o widget com a hora atual
        current_time = QDateTime.currentDateTime()
        self.data_hora_input.setDateTime(current_time)

    def registrar_estacionamento(self):
        vaga_id = self.vaga_combobox.currentData()
        print(type(vaga_id))
        vaga_id = self.db.get_vagas_disponiveis(vaga = vaga_id)
        print(vaga_id[0][0])
        selected_row = self.veiculos_table.currentRow()
        print(selected_row)

        if selected_row == -1:
            QMessageBox.warning(self, 'Erro', 'Selecione um veículo.')
            return

        cliente_veiculo_id = self.veiculos_table.item(selected_row, 0).text()  # Coluna da id

        if not vaga_id or not cliente_veiculo_id:
            QMessageBox.warning(self, 'Erro', 'Selecione a vaga e o veículo.')
            return

        try:
            # Registrar a entrada do veículo
            self.db.estacionar(vaga_id[0][0], cliente_veiculo_id)
            QMessageBox.information(self, 'Sucesso', 'Entrada registrada com sucesso.')
            self.carregar_status_vagas()
            self.preencher_vagas_disponiveis()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', str(e))
    def salvar_alteracoes_usuario(self):
        cpf = self.cpf_cliente_value.text().strip()
        nome = self.nome_cliente_value.text().strip()
        id_cliente = self.cliente_id_
        print(cpf,nome,id_cliente)
        try:
            self.db.salvar_alteracoes(cpf, nome, id_cliente)
            QMessageBox.information(self, 'Sucesso', 'Alterações salvas com sucesso.')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', str(e))
class CadastroVeiculo(JanelaBase):
    def __init__(self, carregar_status_vagas_callback):
        super().__init__("Cadastro Veiculo", 400, 300)
        self.carregar_status_vagas = carregar_status_vagas_callback  # Armazena a função

        # self.setFixedSize(400, 280)
        self.db = Database()
        self.centralizar_janela()

        # self.db = Database()  # Instancia a conexão com o banco de dados

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
        super().__init__("Saída de Veículos", 762, 608)
        self.carregar_status_vagas = carregar_status_vagas_callback  # Armazena a função

        self.db = Database()

        # Layout principal (Horizontal)
        main_layout = QHBoxLayout(self)

        left_layout = QVBoxLayout()

        # CPF input e Botão Filtrar Veículos
        cpf_layout = QHBoxLayout()
        cpf_label = QLabel("Filtrar por CPF:")
        self.cpf_input = QLineEdit()
        self.cpf_input.setPlaceholderText("Digite o CPF")
        self.cpf_input.textChanged.connect(self.filtrar_veiculos)  # Filtro instantâneo

        cpf_layout.addWidget(cpf_label)
        cpf_layout.addWidget(self.cpf_input)

        # Tabela de veículos estacionados
        self.veiculos_table = QTableWidget(0, 5)
        self.veiculos_table.setHorizontalHeaderLabels(["ID", "CPF", "Nome", "Placa", "Vaga"])
        self.veiculos_table.verticalHeader().setVisible(False)

        self.veiculos_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.veiculos_table.setStyleSheet("font-size: 14px; padding: 4px;")

        # Adicionar CPF layout à esquerda
        left_layout.addLayout(cpf_layout)
        left_layout.addWidget(self.veiculos_table)

        # ---- Seção Direita (Informações do Cliente e Ações) ----
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignTop)

        # Data e Hora
        data_hora_label = QLabel("Data e hora de Saída:")
        # data_hora_label.setFont(QFont("Arial", 10))
        self.data_hora_saida_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.data_hora_saida_input.setDisplayFormat("dd/MM/yyyy HH:mm:ss")
        # self.data_hora_saida_input.setFont(QFont("Arial", 10))
        self.data_hora_saida_input.setReadOnly(True)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # Botão de Registrar Saída
        btn_registrar_saida = QPushButton("Registrar Saída")
        # btn_registrar_saida.setFont(QFont("Arial", 10))
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
            # Busca os veículos estacionados no banco
            veiculos_estacionados = self.db.get_veiculos_estacionados()

            # Limpa a tabela antes de mostrar novos dados
            self.veiculos_table.setRowCount(0)

            # Preenche a tabela com os dados retornados
            for veiculo in veiculos_estacionados:
                row_position = self.veiculos_table.rowCount()
                self.veiculos_table.insertRow(row_position)
                self.veiculos_table.setItem(row_position, 0, QTableWidgetItem(str(veiculo[0])))  # ID
                self.veiculos_table.setItem(row_position, 1, QTableWidgetItem(veiculo[1]))  # CPF
                self.veiculos_table.setItem(row_position, 2, QTableWidgetItem(veiculo[2]))  # Nome
                self.veiculos_table.setItem(row_position, 3, QTableWidgetItem(veiculo[3]))  # Placa
                self.veiculos_table.setItem(row_position, 4, QTableWidgetItem(str(veiculo[4])))  # Vaga

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao carregar os veículos: {str(e)}")

    def filtrar_veiculos(self):
        """
        Função para filtrar os veículos estacionados com base no CPF informado.
        """
        filtro_cpf = self.cpf_input.text().strip()

        for row in range(self.veiculos_table.rowCount()):
            item_cpf = self.veiculos_table.item(row, 1)  # CPF está na segunda coluna (indice 1)
            if filtro_cpf in item_cpf.text():
                self.veiculos_table.setRowHidden(row, False)  # Mostra a linha se corresponder ao filtro
            else:
                self.veiculos_table.setRowHidden(row, True)  # Oculta a linha se não corresponder ao filtro

    def update_time(self):
        # Atualiza o widget com a hora atual
        current_time = QDateTime.currentDateTime()
        self.data_hora_saida_input.setDateTime(current_time)

    def registrar_saida(self):
        selected_row = self.veiculos_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Erro', 'Selecione um veículo para registrar a saída.')
            return

        estacionamento_id = self.veiculos_table.item(selected_row, 0).text()  # Coluna do ID de estacionamento

        try:
            # Registrar a saída do veículo no banco de dados
            self.db.registrar_saida(estacionamento_id)
            QMessageBox.information(self, 'Sucesso', 'Saída registrada com sucesso.')
            self.carregar_status_vagas()
            self.carregar_veiculos_estacionados()  # Atualiza a tabela após registrar saída
        except Exception as e:
            QMessageBox.critical(self, 'Erro', str(e))

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
        self.tabela_vagas = QTableWidget(0, 2)
        self.tabela_vagas.setHorizontalHeaderLabels(["Número da Vaga", "Status"])
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
            self.tabela_vagas.setRowCount(0)  # Limpa a tabela antes de preencher

            for vaga in vagas:
                row_position = self.tabela_vagas.rowCount()
                self.tabela_vagas.insertRow(row_position)
                self.tabela_vagas.setItem(row_position, 0, QTableWidgetItem(str(vaga[0])))  # Número da vaga
                self.tabela_vagas.setItem(row_position, 1, QTableWidgetItem(vaga[1]))  # Status (Disponível/Ocupada)

        except Exception as e:
            QMessageBox.critical(self, 'Erro', f"Ocorreu um erro ao carregar as vagas: {str(e)}")

    def adicionar_vaga(self):
        """
        Adiciona uma nova vaga ao banco de dados.
        """
        numero_vaga = self.numero_vaga_input.text().strip()

        if not numero_vaga:
            QMessageBox.warning(self, "Erro", "O número da vaga não pode estar vazio.")
            return

        try:
            # Adicionar a vaga no banco de dados
            self.db.adicionar_vaga(numero_vaga)
            QMessageBox.information(self, "Sucesso", f"A vaga {numero_vaga} foi adicionada com sucesso.")
            self.carregar_vagas_existentes()
            self.carregar_status_vagas()

        except Exception as e:
            QMessageBox.critical(self, 'Erro', f"Erro ao adicionar a vaga: {str(e)}")

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
        self.setGeometry(100, 100, 900, 600)
        self.db = db  # Instância do banco de dados

        # Dados carregados
        self.historico_dados = []

        # Layout principal
        layout = QVBoxLayout(self)

        # ---- Filtros ----
        filtro_layout = QHBoxLayout()

        # Filtro por CPF
        self.input_cpf = QLineEdit()
        self.input_cpf.setPlaceholderText("Filtrar por CPF")
        self.input_cpf.textChanged.connect(self.aplicar_filtros)  # Conectar o filtro ao método aplicar_filtros
        filtro_layout.addWidget(self.input_cpf)

        # Filtro por Placa
        self.input_placa = QLineEdit()
        self.input_placa.setPlaceholderText("Filtrar por Placa")
        self.input_placa.textChanged.connect(self.aplicar_filtros)  # Conectar o filtro ao método aplicar_filtros
        filtro_layout.addWidget(self.input_placa)

        # Filtro por Nome
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Filtrar por Nome")
        self.input_nome.textChanged.connect(self.aplicar_filtros)  # Conectar o filtro ao método aplicar_filtros
        filtro_layout.addWidget(self.input_nome)

        layout.addLayout(filtro_layout)

        # ---- Tabela de Histórico ----
        self.table_historico = QTableWidget(0, 9)
        self.table_historico.setHorizontalHeaderLabels(
            ["CPF", "Nome", "Marca", "Modelo", "Placa", "Vaga", "Entrada", "Saída", "Tempo"]
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
            self.historico_dados = self.db.get_historico()  # Obter os dados do banco de dados
            self.table_historico.setRowCount(0)  # Limpar a tabela antes de inserir novos dados

            # Preencher a tabela com os dados retornados
            for registro in self.historico_dados:
                row_position = self.table_historico.rowCount()
                self.table_historico.insertRow(row_position)
                self.table_historico.setItem(row_position, 0, QTableWidgetItem(str(registro[0])))  # CPF
                self.table_historico.setItem(row_position, 1, QTableWidgetItem(registro[1]))  # Nome Completo
                self.table_historico.setItem(row_position, 2, QTableWidgetItem(registro[2]))  # Marca
                self.table_historico.setItem(row_position, 3, QTableWidgetItem(registro[3]))  # Modelo
                self.table_historico.setItem(row_position, 4, QTableWidgetItem(registro[4]))  # Placa
                self.table_historico.setItem(row_position, 5, QTableWidgetItem(registro[5]))  # Vaga
                self.table_historico.setItem(row_position, 6, QTableWidgetItem(str(registro[6])))  # Data/Hora Entrada
                self.table_historico.setItem(row_position, 7, QTableWidgetItem(str(registro[7]) if registro[7] else "-"))  # Data/Hora Saída
                self.table_historico.setItem(row_position, 8, QTableWidgetItem(str(registro[8]) if registro[8] else "-"))  # Tempo de Permanência

        except Exception as e:
            QMessageBox.critical(self, 'Erro', f"Erro ao carregar o histórico: {str(e)}")

    def aplicar_filtros(self):
        """
        Aplica os filtros sobre os dados carregados e atualiza a tabela.
        """
        cpf_filtro = self.input_cpf.text().strip().lower()
        placa_filtro = self.input_placa.text().strip().lower()
        nome_filtro = self.input_nome.text().strip().lower()

        self.table_historico.setRowCount(0)  # Limpar a tabela antes de aplicar os filtros

        for registro in self.historico_dados:
            cpf = str(registro[0]).lower()
            nome = str(registro[1]).lower()
            placa = str(registro[4]).lower()

            # Verifica se o registro atende aos filtros
            if (cpf_filtro in cpf and
                placa_filtro in placa and
                nome_filtro in nome):
                row_position = self.table_historico.rowCount()
                self.table_historico.insertRow(row_position)

                self.table_historico.setItem(row_position, 0, QTableWidgetItem(str(registro[0])))  # CPF
                self.table_historico.setItem(row_position, 1, QTableWidgetItem(registro[1]))  # Nome Completo
                self.table_historico.setItem(row_position, 2, QTableWidgetItem(registro[2]))  # Marca
                self.table_historico.setItem(row_position, 3, QTableWidgetItem(registro[3]))  # Modelo
                self.table_historico.setItem(row_position, 4, QTableWidgetItem(registro[4]))  # Placa
                self.table_historico.setItem(row_position, 5, QTableWidgetItem(registro[5]))  # Vaga
                self.table_historico.setItem(row_position, 6, QTableWidgetItem(str(registro[6])))  # Data/Hora Entrada
                self.table_historico.setItem(row_position, 7, QTableWidgetItem(str(registro[7]) if registro[7] else "-"))  # Data/Hora Saída
                self.table_historico.setItem(row_position, 8, QTableWidgetItem(str(registro[8]) if registro[8] else "-"))  # Tempo de Permanência

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configurações da janela principal
        self.setWindowTitle("Sistema de Estacionamento")
        self.setGeometry(380, 130, 1169, 828)  # (x, y, largura, altura)

        self.centralizar_janela()
        self.db = Database()  # Instanciação do banco de dados

        hbox_buttons = QHBoxLayout()

        # Campo de pesquisa de Placa
        self.input_placa = QLineEdit()
        self.input_placa.setPlaceholderText("Pesquisar Placa")
        self.input_placa.textChanged.connect(self.filtrar_por_placa)
        self.input_placa.setStyleSheet("padding: 5px;")
        hbox_buttons.addWidget(self.input_placa)

        # Botões de controle
        self.btn_entrada = QPushButton("ENTRADA")
        self.btn_entrada.clicked.connect(self.create_entrada_section)
        self.btn_saida = QPushButton("SAÍDA")
        self.btn_saida.clicked.connect(self.create_saida_section)
        self.btn_historico = QPushButton("HISTÓRICO")
        self.btn_historico.clicked.connect(self.create_historico_section)

        self.btn_entrada.setFixedSize(QSize(120, 40))
        self.btn_saida.setFixedSize(QSize(120, 40))
        self.btn_historico.setFixedSize(QSize(120, 40))
        hbox_buttons.addWidget(self.btn_entrada)
        hbox_buttons.addWidget(self.btn_saida)
        hbox_buttons.addWidget(self.btn_historico)
        hbox_buttons.setAlignment(Qt.AlignTop)
        hbox_buttons.setContentsMargins(10, 0, 10, 10)

        # Criação do container para os botões
        buttons_container = QWidget()
        buttons_container.setLayout(hbox_buttons)

        # Adiciona o container dos botões e a tabela ao layout vertical principal
        vbox_main = QVBoxLayout()
        vbox_main.addWidget(buttons_container)

        # Adicionando Tabela para mostrar status das vagas
        self.vagas_table = QTableWidget(0, 6)
        self.vagas_table.setHorizontalHeaderLabels(["Vaga", "Status", "Placa", "Cliente", "Horário de Entrada","Tempo"])
        header = self.vagas_table.horizontalHeader()
        header.setMinimumSectionSize(100)  # Ajuste o valor conforme necessário

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        # As outras colunas irão preencher o espaço restante
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Coluna "Placa"
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Coluna "Cliente"
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Coluna "Horário de Entrada"
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Coluna "Tempo"

        self.vagas_table.verticalHeader().setVisible(False)

        vbox_main.addWidget(self.vagas_table)

        # Definindo o layout no container principal da janela
        self.container = QWidget()
        self.container.setLayout(vbox_main)
        self.setCentralWidget(self.container)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizar_tempo_decorrido)
        self.timer.start(1000)  #1000ms = 1s

        self.carregar_status_vagas()
        # Menu de cadastro de clientes
        menu = self.menuBar()
        menu_cliente = menu.addMenu("Cliente")
        menu_config_vagas = menu.addMenu("Configurar Vagas")
        # menu.setStyleSheet("""
        #     QMenuBar {
        #         background-color: #2c3e50;
        #         color: white;
        #         font-size: 16px;
        #         padding: 5px;
        #         border-bottom: 2px solid #2980b9;
        #     }
        #     QMenuBar::item {
        #         padding: 8px 20px;
        #         background-color: transparent;
        #         color: white;
        #         border-radius: 5px;
        #     }
        #     QMenuBar::item:selected {
        #         background-color: #2980b9;
        #         color: #ecf0f1;
        #     }
        #     QMenu {
        #         background-color: #34495e;
        #         color: white;
        #         border: 1px solid #2980b9;
        #         margin: 2px;
        #     }
        #     QMenu::item {
        #         padding: 8px 25px;
        #         border-radius: 5px;
        #     }
        #     QMenu::item:selected {
        #         background-color: #2980b9;
        #         color: #ecf0f1;
        #     }
        #     QMenu::separator {
        #         height: 2px;
        #         background: #7f8c8d;
        #         margin-left: 10px;
        #         margin-right: 10px;
        #     }
        # """)

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
            item_placa = self.vagas_table.item(row, 2)  # Coluna da Placa (índice 2)
            if filtro_placa in item_placa.text().lower():
                self.vagas_table.setRowHidden(row, False)  # Mostra a linha se corresponder ao filtro
            else:
                self.vagas_table.setRowHidden(row, True)  # Oculta a linha se não corresponder

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
            vagas = self.db.get_status_vagas()  # Obtém os status das vagas
            self.vagas_table.setRowCount(0)  # Limpar a tabela antes de inserir novos dados

            # Preencher a tabela com os dados
            for vaga in vagas:
                row_position = self.vagas_table.rowCount()
                self.vagas_table.insertRow(row_position)
                vaga_id_item = QTableWidgetItem()
                vaga_id_item.setData(Qt.DisplayRole, int(vaga[0]))
                self.vagas_table.setItem(row_position, 0, vaga_id_item)  # Vaga ID

                self.vagas_table.setItem(row_position, 1, QTableWidgetItem(vaga[1]))  # Status (Disponível/Ocupada)
                self.vagas_table.setItem(row_position, 2, QTableWidgetItem(vaga[2]))  # Placa
                self.vagas_table.setItem(row_position, 3, QTableWidgetItem(vaga[3]))  # Cliente
                self.vagas_table.setItem(row_position, 4, QTableWidgetItem(vaga[4]))  # Horário de Entrada
            self.vagas_table.sortItems(0, Qt.AscendingOrder)  # Ordena pela coluna 0 (Vaga ID) em ordem crescente
            self.atualizar_tempo_decorrido()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f"Ocorreu um erro ao carregar o status das vagas: {str(e)}")

    def atualizar_tempo_decorrido(self):
        """
        Atualiza a coluna de tempo decorrido apenas para as vagas ocupadas.
        """
        try:
            current_time = QDateTime.currentDateTime()  # Hora atual do sistema

            for row in range(self.vagas_table.rowCount()):
                status_item = self.vagas_table.item(row, 1)  # Pega o item da coluna "Status"
                if status_item and status_item.text() == "Ocupada":  # Verifica se a vaga está ocupada
                    horario_entrada_item = self.vagas_table.item(row, 4)  # Pega o item na coluna "Horário de Entrada"
                    if horario_entrada_item:
                        horario_entrada_str = horario_entrada_item.text()  # Extrai o texto do horário de entrada

                        # Tentativa de converter o horário usando formatos possíveis
                        horario_entrada = QDateTime.fromString(horario_entrada_str, "yyyy-MM-dd HH:mm:ss")
                        if not horario_entrada.isValid():
                            horario_entrada = QDateTime.fromString(horario_entrada_str, "dd/MM/yyyy HH:mm:ss")

                        if horario_entrada.isValid():  # Verifica se o horário de entrada é válido
                            # Calcula o tempo decorrido em segundos
                            tempo_decorrido = horario_entrada.secsTo(current_time)
                            horas = tempo_decorrido // 3600
                            minutos = (tempo_decorrido % 3600) // 60
                            segundos = tempo_decorrido % 60

                            # Formata o tempo decorrido em horas, minutos e segundos
                            tempo_formatado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
                            self.vagas_table.setItem(row, 5, QTableWidgetItem(
                                tempo_formatado))  # Atualiza a coluna de Tempo Decorrido
                        else:
                            self.vagas_table.setItem(row, 5,
                                                     QTableWidgetItem("Hora Inválida"))  # Caso o horário seja inválido
                    else:
                        self.vagas_table.setItem(row, 5,
                                                 QTableWidgetItem("Sem Horário"))  # Caso não haja horário de entrada
                else:
                    self.vagas_table.setItem(row, 5,
                                             QTableWidgetItem(""))  # Limpa a coluna "Tempo" para vagas disponíveis

        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao atualizar o tempo decorrido: {str(e)}")

    def create_cliente_section(self):
        # Criar e exibir a nova janela de cadastro
        self.janela_cadastro = JanelaCadastroCliente(self.carregar_status_vagas)
        self.janela_cadastro.exec_()

    def create_entrada_section(self):
        # Criar e exibir a nova janela de cadastro
        self.janela_entrada = JanelaEntrada(self.carregar_status_vagas)
        self.janela_entrada.exec_()

    def create_saida_section(self):
        # Criar e exibir a nova janela de cadastro
        self.janela_saida = JanelaSaida(self.carregar_status_vagas)
        self.janela_saida.exec_()
    def create_configuracao_section(self):
        # Criar e exibir a nova janela de cadastro
        self.janela_configuracao = JanelaConfigurarVagas(self.carregar_status_vagas)
        self.janela_configuracao.exec_()

    def create_historico_section(self):
        # Criar uma nova janela para exibir o histórico de entradas/saídas
        self.janela_historico = JanelaHistorico(self.db)
        self.janela_historico.exec_()

