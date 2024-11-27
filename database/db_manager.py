import psycopg2
from config.settings import DB_CONFIG
from datetime import datetime, timedelta

class Database:
    _instance = None  # Variável de classe para armazenar a instância

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._connect()  # Chama a função de conexão ao banco de dados
        return cls._instance

    def _connect(self):
        # Conectar ao banco de dados PostgreSQL
        try:
            self.connection = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor()
            print("Conexão com o banco de dados estabelecida.")
        except Exception as e:
            raise ConnectionError(f"Erro ao conectar ao banco de dados: {str(e)}")

    def get_cliente_by_cpf(self,cpf):
        cpf = str(cpf).strip()

        # Validação do CPF
        if not cpf or not cpf.isdigit() or len(cpf) != 11:
            raise ValueError("CPF inválido. O CPF deve conter exatamente 11 dígitos numéricos.")

        try:
            # Executa a consulta SQL para buscar o cliente pelo CPF
            self.cursor.execute("""
                SELECT id
                FROM cliente
                WHERE cpf = %s
            """, (cpf,))

            cliente = self.cursor.fetchone()

            # Verifica se o cliente foi encontrado
            if not cliente:
                raise ValueError(f"Cliente com o CPF {cpf} não encontrado.")

            return cliente

        except psycopg2.DatabaseError as e:
            self.connection.rollback()
            raise ValueError(f"Erro ao buscar o cliente no banco de dados: {str(e)}")
    def registrar_cliente(self, cpf, nome_completo):
        print(f"Tentando registrar cliente: CPF={cpf}, Nome={nome_completo}")
        if not cpf or not cpf.isdigit() or len(cpf) != 11:
            raise ValueError("CPF inválido.")
        if not nome_completo.strip():
            raise ValueError("Nome completo é obrigatório.")

        try:
            self.cursor.execute("""
                INSERT INTO cliente (cpf, nome_completo) VALUES (%s, %s);
            """, (cpf, nome_completo))
            self.connection.commit()
            print("Cliente registrado com sucesso.")
        except psycopg2.IntegrityError:
            self.connection.rollback()
            print("Erro: Cliente já existe.")
            raise ValueError("Cliente com este CPF já existe.")

    def registrar_veiculo(self, cliente_id, marca_veiculo, modelo_veiculo, placa):
        print(f"Tentando registrar veículo: Cliente_ID={cliente_id}, Marca={marca_veiculo}, Modelo={modelo_veiculo}, Placa={placa}")
        # Validação básica
        if not cliente_id or not isinstance(cliente_id, int):
            raise ValueError("ID do cliente inválido.")
        if not marca_veiculo.strip():
            raise ValueError("Marca do veículo é obrigatória.")
        if not modelo_veiculo.strip():
            raise ValueError("Modelo do veículo é obrigatório.")
        if not placa.strip() or len(placa) != 7:
            raise ValueError("Placa inválida. Deve conter exatamente 7 caracteres.")

        try:
            # Inserir o veículo na tabela cliente_veiculo
            self.cursor.execute("""
                INSERT INTO cliente_veiculo (cliente_id, marca_veiculo, modelo_veiculo, placa)
                VALUES (%s, %s, %s, %s);
            """, (cliente_id, marca_veiculo, modelo_veiculo, placa))
            self.connection.commit()
            print("Veículo registrado com sucesso.")
        except psycopg2.IntegrityError:
            self.connection.rollback()
            print("Erro: Veículo já existe ou cliente não existe.")
            raise ValueError("Veículo com esta placa já existe ou cliente não existe.")
        except Exception as e:
            self.connection.rollback()
            print(f"Erro ao registrar veículo: {str(e)}")
            raise RuntimeError(f"Erro ao registrar o veículo: {str(e)}")

    def get_veiculo_do_cliente(self, cpf):
        cpf = str(cpf)
        print(f"Buscando veículos para o CPF={cpf}")
        if not cpf or not cpf.isdigit() or len(cpf) != 11:
            raise ValueError("CPF inválido.")

        try:
            # Execute a query para buscar os veículos associados ao cliente
            self.cursor.execute("""
                SELECT cv.id,c.cpf, c.nome_completo, cv.marca_veiculo, cv.modelo_veiculo, cv.placa,c.id
                FROM cliente c
                INNER JOIN cliente_veiculo cv ON c.id = cv.cliente_id
                WHERE c.cpf = %s""", (cpf,))

            veiculos = self.cursor.fetchall()
            print(f"Veículos encontrados: {veiculos}")
            # Verifica se há veículos retornados
            if not veiculos:
                print("Nenhum veículo encontrado.")
                raise ValueError("Cliente com esse CPF não existe ou não tem veículos cadastrados.")

            return veiculos

        except psycopg2.DatabaseError as e:
            self.connection.rollback()
            print(f"Erro ao buscar veículos: {str(e)}")
            raise ValueError(f"Erro ao buscar veículos do cliente: {str(e)}")

    def insert_client_veiculo(self, cpf, marca_veiculo, modelo_veiculo, placa):
        cliente_id = self.get_cliente_by_cpf(cpf)
        print(cliente_id)
        print(f"Tentando inserir veículo para o cliente {cliente_id}")
        try:
            # Verifica se os campos obrigatórios foram preenchidos
            if not (cliente_id and marca_veiculo and modelo_veiculo and placa):
                raise ValueError("Todos os campos devem ser preenchidos.")

            # Inserir veículo no banco de dados
            self.cursor.execute("""
                INSERT INTO cliente_veiculo (cliente_id, marca_veiculo, modelo_veiculo, placa)
                VALUES (%s, %s, %s, %s);
            """, (cliente_id, marca_veiculo, modelo_veiculo, placa))
            self.connection.commit()
            print("Veículo inserido com sucesso.")

        except psycopg2.IntegrityError as e:
            # Violação de integridade, como chave estrangeira ou valor duplicado
            self.connection.rollback()
            print(f"Erro de integridade: {str(e)}")
            if "duplicate key" in str(e):
                raise ValueError(f"Erro: O veículo com a placa '{placa}' já está cadastrado.")
            else:
                raise ValueError(f"Erro de integridade ao registrar o veículo: {str(e)}")

        except psycopg2.DatabaseError as e:
            # Erros relacionados ao banco de dados
            self.connection.rollback()
            print(f"Erro de banco de dados: {str(e)}")
            raise RuntimeError(f"Erro no banco de dados: {str(e)}")

        except ValueError as e:
            # Erros de validação, como campos vazios ou inválidos
            print(f"Erro de validação: {str(e)}")
            raise ValueError(f"Erro de validação: {str(e)}")

        except Exception as e:
            # Outros erros inesperados
            self.connection.rollback()
            print(f"Erro inesperado: {str(e)}")
            raise RuntimeError(f"Erro inesperado ao registrar o veículo: {str(e)}")

    def estacionar(self, vaga_id, cliente_veiculo_id, data_hora_entrada=None, status=None, tempo_limite=None):
        """
        Função para registrar a entrada de um veículo no estacionamento.
        """
        vaga_id, cliente_veiculo_id = int(vaga_id), int(cliente_veiculo_id)
        status = status or 'ativo'
        data_hora_entrada = data_hora_entrada or datetime.now()

        try:
            # Verificar se já existe um registro 'ativo' para o cliente_veiculo_id
            self.cursor.execute("""
                SELECT id FROM estacionamento
                WHERE cliente_veiculo_id = %s AND status = 'ativo';
            """, (cliente_veiculo_id,))

            veiculo_ativo = self.cursor.fetchone()

            if veiculo_ativo:
                raise ValueError(f"O veículo com ID {cliente_veiculo_id} já está estacionado com o status 'ativo'.")

            # Registrar a entrada do veículo, incluindo tempo_limite
            self.cursor.execute("""
                INSERT INTO estacionamento (vaga_id, cliente_veiculo_id, data_hora_entrada, status, tempo_limite)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (vaga_id, cliente_veiculo_id, data_hora_entrada, status, tempo_limite))

            estacionamento_id = self.cursor.fetchone()[0]
            self.connection.commit()

            # Atualizar o status da vaga para 'ocupada'
            self.cursor.execute("UPDATE vagas SET status = 'ocupada' WHERE id = %s", (vaga_id,))
            self.connection.commit()

            print(f"Veículo estacionado com sucesso. Estacionamento ID: {estacionamento_id}")
            return estacionamento_id

        except Exception as e:
            self.connection.rollback()
            print(f"Erro ao registrar o estacionamento: {str(e)}")
            raise RuntimeError(f"Erro ao registrar o estacionamento: {str(e)}")

    def get_vagas_disponiveis(self,vaga=None,tipo=None,tipos_de_vagas_atuais=None):
        print(f"Buscando vagas disponíveis (Filtro: {vaga})")
        if vaga:
            vaga = str(vaga)
            self.cursor.execute("SELECT id FROM vagas WHERE numero_vaga = %s ", (vaga,))
            resultado = self.cursor.fetchall()

            print(f"id da vaga {vaga}: {resultado}")
            return resultado
        elif tipo:
            tipo = str(tipo)
            self.cursor.execute("SELECT id,numero_vaga FROM vagas WHERE tipo = %s and status = 'disponivel'", (tipo,))
            resultado = self.cursor.fetchall()

            print(f"id da vaga {tipo}: {resultado}")
            return resultado
        elif tipos_de_vagas_atuais:
            tipos_de_vagas_atuais = str(tipos_de_vagas_atuais)
            self.cursor.execute("SELECT distinct tipo FROM vagas where status = 'disponivel'")
            resultado = self.cursor.fetchall()

            print(f"id da vaga {tipos_de_vagas_atuais}: {resultado}")
            return resultado
        else:
            self.cursor.execute("SELECT numero_vaga, status,tipo  FROM vagas WHERE status = 'disponivel';")
            vagas = self.cursor.fetchall()
            vagas = sorted(vagas, key=lambda x: int(x[0]))

            print(f"Vagas disponíveis: {vagas}")
            return vagas
    def salvar_alteracoes(self, cpf, nome_completo, cliente_id):
        print(f"Iniciando atualização do cliente com ID={cliente_id}: CPF={cpf}, Nome={nome_completo}")

        # Validação do CPF
        if not cpf or not cpf.isdigit() or len(cpf) != 11:
            raise ValueError("CPF inválido. O CPF deve conter exatamente 11 dígitos numéricos.")

        # Validação do Nome Completo
        if not nome_completo.strip():
            raise ValueError("O campo 'Nome completo' é obrigatório.")

        try:
            # Atualizando o cliente no banco de dados
            print(f"Executando atualização no banco para o cliente com ID={cliente_id}.")
            self.cursor.execute("""
                UPDATE cliente 
                SET nome_completo = %s, cpf = %s 
                WHERE id = %s
            """, (nome_completo, cpf, cliente_id))

            self.connection.commit()
            print(f"Cliente com ID={cliente_id} atualizado com sucesso. CPF={cpf}, Nome={nome_completo}")

        except psycopg2.IntegrityError:
            self.connection.rollback()
            print(f"Erro de integridade: O CPF {cpf} já está registrado no sistema.")
            raise ValueError("Erro: Já existe um cliente cadastrado com este CPF.")

        except Exception as e:
            self.connection.rollback()
            print(f"Erro inesperado ao atualizar o cliente com ID={cliente_id}. Detalhes: {str(e)}")
            raise RuntimeError(f"Erro inesperado: {str(e)}")

    def registrar_saida(self, estacionamento_id,saida=False):
        """
        Função para registrar a saída de um veículo.
        Parâmetros:
            estacionamento_id: ID da entrada de estacionamento (único para cada entrada/saída).
        """
        try:
            # Verificar se o estacionamento está ativo antes de registrar a saída
            self.cursor.execute("SELECT status, data_hora_entrada FROM estacionamento WHERE id = %s",
                                (estacionamento_id,))
            result = self.cursor.fetchone()

            if not result:
                raise ValueError("Registro de estacionamento não encontrado.")

            status, data_hora_entrada = result
            if status != 'ativo':
                raise ValueError(f"O estacionamento com ID {estacionamento_id} já foi concluído ou está inativo.")

            # Obter a data e hora atuais para a saída
            data_hora_saida = datetime.now()

            # Calcular o tempo de permanência
            tempo_permanencia = data_hora_saida - data_hora_entrada
            if saida:
                # Atualizar a saída do veículo no banco de dados
                self.cursor.execute("""
                    UPDATE estacionamento
                    SET data_hora_saida = %s, status = 'concluido',
                        tempo_permanencia = TO_CHAR(%s, 'HH24:MI:SS')
                    WHERE id = %s AND status = 'ativo';
                """, (data_hora_saida, tempo_permanencia, estacionamento_id))
                self.connection.commit()

                # Atualizar a vaga associada para disponível
                self.cursor.execute("""
                    UPDATE vagas
                    SET status = 'disponivel'
                    WHERE id = (SELECT vaga_id FROM estacionamento WHERE id = %s);
                """, (estacionamento_id,))
                self.connection.commit()

                print(f"Saída registrada com sucesso para o estacionamento ID {estacionamento_id}.")
                return True
            else:
                # Calcular o tempo de permanência
                tempo_permanencia = data_hora_saida - data_hora_entrada
                #formatar tempo permanencia para HH:MM:SS
                tempo_permanencia = str(tempo_permanencia).split(".")[0]
                print(tempo_permanencia)
                # Retornar o tempo limite e o tempo de permanência
                temp_l = self.cursor.execute("SELECT tempo_limite FROM estacionamento WHERE id = %s", (estacionamento_id,))
                tempo_limite = self.cursor.fetchone()[0]

                return tempo_permanencia,tempo_limite

        except Exception as e:
            self.connection.rollback()
            raise RuntimeError(f"Erro ao registrar a saída: {str(e)}")

    def get_veiculos_estacionados(self):
        """
        Função para buscar os veículos que estão estacionados (status = 'ativo').
        """
        self.cursor.execute("""
    SELECT estacionamento.id, cliente.cpf, cliente.nome_completo, cliente_veiculo.placa,v.numero_vaga
    FROM estacionamento
    inner JOIN cliente_veiculo ON estacionamento.cliente_veiculo_id = cliente_veiculo.id
    inner JOIN cliente ON cliente_veiculo.cliente_id = cliente.id
    inner join vagas v on estacionamento.vaga_id = v.id
    WHERE estacionamento.status = 'ativo'
        """)
        return self.cursor.fetchall()
    def get_usuarios(self):
        """
        Função para buscar os usuários do sistema.
        """
        self.cursor.execute("SELECT * FROM cliente")
        return self.cursor.fetchall()

    def get_status_vagas(self):
        """
        Retorna o status de todas as vagas, incluindo informações do veículo e cliente, se estiver ocupada.
        """
        try:
            query = """
                SELECT 
                    v.numero_vaga AS vaga_id, 
                    CASE 
                        WHEN e.id IS NOT NULL THEN 'Ocupada' 
                        ELSE 'Disponível' 
                    END AS status_vaga,
                    v.tipo as tipo_vaga,
                    COALESCE(c.placa, '-') AS placa_veiculo,
                    COALESCE(cli.nome_completo, '-') AS nome_cliente,
                    TO_CHAR(e.data_hora_entrada, 'DD/MM/YYYY HH24:MI:SS') AS horario_entrada,
                    e.tempo_limite as tempo_limite
                FROM vagas v
                LEFT JOIN estacionamento e ON v.id = e.vaga_id AND e.status = 'ativo'
                LEFT JOIN cliente_veiculo c ON e.cliente_veiculo_id = c.id
                LEFT JOIN cliente cli ON c.cliente_id = cli.id
                ORDER BY v.id;
            """
            self.cursor.execute(query)
            vagas = self.cursor.fetchall()  # Obtém todas as vagas com seus respectivos status e dados associados
            print(vagas)
            return vagas

        except psycopg2.DatabaseError as e:
            print(f"Erro ao buscar status das vagas: {e}")
            return []

        finally:
            self.connection.commit()

    def adicionar_vaga(self, numero_vaga,tipo_vaga):
        """
        Adiciona uma nova vaga ao estacionamento, com validação de dados.
        """
        # Verificar se o número da vaga é válido
        if not numero_vaga or not numero_vaga.strip():
            raise ValueError("O número da vaga não pode ser vazio.")

        # Verificar se a vaga já existe
        try:
            self.cursor.execute("SELECT COUNT(*) FROM vagas WHERE numero_vaga = %s;", (numero_vaga,))
            resultado = self.cursor.fetchone()

            if resultado[0] > 0:
                raise ValueError(f"A vaga {numero_vaga} já está cadastrada no sistema.")

            # Inserir a nova vaga
            self.cursor.execute(
                """
                INSERT INTO vagas (numero_vaga, status,tipo)
                VALUES (%s, 'disponivel',%s);
            """,
                (numero_vaga,tipo_vaga))
            self.connection.commit()

        except psycopg2.DatabaseError as e:
            self.connection.rollback()
            raise Exception(f"Erro no banco de dados ao adicionar a vaga: {str(e)}")

        except Exception as e:
            raise Exception(f"Erro ao adicionar vaga: {str(e)}")

    def remover_vaga(self, numero_vaga):
        """
        Remove uma vaga do estacionamento, com validação de dados e tratamento de exceções.
        """
        # Verificar se o número da vaga é válido
        if not numero_vaga or not numero_vaga.strip():
            raise ValueError("O número da vaga não pode ser vazio.")

        try:
            # Verificar se a vaga existe
            self.cursor.execute("SELECT id FROM vagas WHERE numero_vaga = %s;", (numero_vaga,))
            vaga_result = self.cursor.fetchone()

            if not vaga_result:
                raise ValueError(f"A vaga {numero_vaga} não foi encontrada no sistema.")

            vaga_id = vaga_result[0]

            # Verificar se a vaga está associada a algum estacionamento ativo
            self.cursor.execute("SELECT COUNT(*) FROM estacionamento WHERE vaga_id = %s AND status = 'ativo';",
                                (vaga_id,))
            veiculos_estacionados = self.cursor.fetchone()[0]

            if veiculos_estacionados > 0:
                raise ValueError(
                    f"A vaga {numero_vaga} está associada a {veiculos_estacionados} veículos em estacionamento ativo. Não é possível removê-la.")

            # Remover a vaga
            self.cursor.execute("DELETE FROM vagas WHERE numero_vaga = %s;", (numero_vaga,))
            self.connection.commit()

        except psycopg2.DatabaseError as e:
            self.connection.rollback()
            raise Exception(f"Erro no banco de dados ao remover a vaga: {str(e)}")

        except Exception as e:
            raise Exception(f"Erro ao remover vaga: {str(e)}")
    def get_historico(self):
        """
        Retorna os registros de entrada e saida do estacionamento.
        """
        try:
            self.cursor.execute("""        SELECT
    c.cpf AS CPF,
    c.nome_completo AS NOME_COMPLETO,
    cv.marca_veiculo AS MARCA,
    cv.modelo_veiculo AS MODELO,
    cv.placa AS PLACA,
    v.numero_vaga AS VAGA,
    e.data_hora_entrada,
    e.data_hora_saida,
    e.tempo_limite,
    e.tempo_permanencia,
    e.status AS status_estacionamento,
    p.valor_pago as valor_pago
FROM
    estacionamento e
JOIN
    cliente_veiculo cv ON e.cliente_veiculo_id = cv.id
JOIN
    cliente c ON cv.cliente_id = c.id
JOIN
    vagas v ON e.vaga_id = v.id
JOIN pagamentos p ON e.id = p.estacionamento_id
ORDER BY
    e.data_hora_entrada DESC;""")
            historico = self.cursor.fetchall()
            print(historico)
            return historico
        except Exception as e:
            raise Exception(f"Erro ao buscar historico: {str(e)}")
    def fechar_conexao(self):
        print("Fechando conexão com o banco de dados.")
        self.cursor.close()
        self.connection.close()

    def get_precificacao(self,tempo_limite,tempos_definidos = False):

        if tempos_definidos:
            try:
                self.cursor.execute("SELECT tempo FROM precificação")
                tempos = self.cursor.fetchall()
                # converter para uma lista
                tempos = [tempo[0] for tempo in tempos]
                return tempos
            except Exception as e:
                raise Exception(f"Erro ao buscar tempo: {str(e)}")
        if tempo_limite:
            try:
                self.cursor.execute("SELECT preço FROM precificação WHERE tempo = %s;", (tempo_limite,))
                preco = self.cursor.fetchone()
                return preco
            except Exception as e:
                raise Exception(f"Erro ao buscar preço: {str(e)}")
    def get_tipos_vagas(self):
        """
        Retorna uma lista com os tipos de vagas disponíveis.
        """
        try:
            self.cursor.execute("SELECT DISTINCT tipo FROM vagas WHERE status = 'disponivel';")
            tipos_vagas = self.cursor.fetchall()
            # Extrai apenas os valores (primeiro elemento de cada tupla)
            return [tipo[0] for tipo in tipos_vagas]
        except Exception as e:
            raise Exception(f"Erro ao buscar tipos de vagas: {str(e)}")

    def get_dados_pagamento(self, estacionamento_id):
        """
        Retorna os dados necessários para a tela de pagamentos.
        Parâmetros:
            estacionamento_id (int): ID do estacionamento ativo.
        Retorno:
            dict: Informações do cliente, veículo, vaga e valores para pagamento.
        """
        try:
            # Busca informações principais do estacionamento
            self.cursor.execute("""
                SELECT 
                    c.cpf, c.nome_completo, 
                    cv.marca_veiculo, cv.modelo_veiculo, cv.placa, 
                    v.numero_vaga, e.data_hora_entrada, e.tempo_limite
                FROM estacionamento e
                INNER JOIN cliente_veiculo cv ON e.cliente_veiculo_id = cv.id
                INNER JOIN cliente c ON cv.cliente_id = c.id
                INNER JOIN vagas v ON e.vaga_id = v.id
                WHERE e.id = %s AND e.status = 'ativo';
            """, (estacionamento_id,))

            resultado = self.cursor.fetchone()
            if not resultado:
                raise ValueError("Estacionamento não encontrado ou já concluído.")

            # Extrai os dados do resultado
            cpf, nome, marca, modelo, placa, vaga, entrada, tempo_limite = resultado

            # Calcula o tempo de permanência
            data_hora_saida = datetime.now()
            tempo_permanencia = data_hora_saida - entrada
            tempo_permanencia_str = str(tempo_permanencia).split(".")[0]  # Formata para HH:MM:SS

            # Obtém o valor base associado ao tempo limite
            self.cursor.execute("SELECT preço FROM precificação WHERE tempo = %s;", (tempo_limite,))
            valor_base = self.cursor.fetchone()
            if not valor_base:
                raise ValueError("Precificação não definida para o tempo limite especificado.")
            valor_base = float(valor_base[0])  # Certifica-se de que é float

            # Calcula o valor excedente, se aplicável
            tempo_limite_td = timedelta(hours=int(tempo_limite.split(":")[0]),
                                        minutes=int(tempo_limite.split(":")[1]),
                                        seconds=int(tempo_limite.split(":")[2]))

            if tempo_permanencia > tempo_limite_td:
                delta = tempo_permanencia - tempo_limite_td
                horas_excedidas = delta.total_seconds() // 3600 + (1 if delta.total_seconds() % 3600 > 0 else 0)
                valor_excedente = horas_excedidas * 10  # Cobrança adicional por hora excedida
            else:
                valor_excedente = 0

            # Valor final a pagar
            valor_total = valor_base + valor_excedente

            # Retorna um dicionário com os dados necessários
            return {
                "cliente": {"cpf": cpf, "nome": nome},
                "veiculo": {"marca": marca, "modelo": modelo, "placa": placa},
                "vaga": vaga,
                "tempo_permanencia": tempo_permanencia_str,
                "tempo_limite": tempo_limite,
                "valor_base": valor_base,
                "valor_excedente": valor_excedente,
                "valor_total": valor_total
            }

        except Exception as e:
            raise RuntimeError(f"Erro ao buscar dados para pagamento: {str(e)}")

    def registrar_pagamento(self, estacionamento_id, valor_pago):
        """
        Registra um pagamento no banco de dados.

        Parâmetros:
            estacionamento_id (int): ID do estacionamento associado ao pagamento.
            valor_pago (float): Valor pago pelo cliente.

        Exceções:
            ValueError: Caso o estacionamento_id ou valor_pago sejam inválidos.
            RuntimeError: Caso ocorra algum erro durante o registro no banco de dados.
        """
        try:
            # Validação básica
            try:
                estacionamento_id = int(estacionamento_id)
            except (ValueError, TypeError):
                raise ValueError("ID do estacionamento inválido. Deve ser um número inteiro.")

            if not valor_pago or not isinstance(valor_pago, (float, int)) or valor_pago <= 0:
                raise ValueError("Valor pago inválido. Deve ser um número positivo.")
            # Insere o pagamento no banco de dados
            self.cursor.execute("""
                INSERT INTO pagamentos (estacionamento_id, valor_pago)
                VALUES (%s, %s)
                RETURNING id;
            """, (estacionamento_id, valor_pago))

            pagamento_id = self.cursor.fetchone()[0]
            self.connection.commit()

            print(f"Pagamento registrado com sucesso. ID do pagamento: {pagamento_id}")
            return pagamento_id

        except psycopg2.IntegrityError as e:
            self.connection.rollback()
            print(f"Erro de integridade ao registrar pagamento: {str(e)}")
            raise ValueError("Erro de integridade ao registrar pagamento. Verifique se o estacionamento está ativo.")

        except Exception as e:
            self.connection.rollback()
            print(f"Erro ao registrar pagamento: {str(e)}")
            raise RuntimeError(f"Erro ao registrar pagamento: {str(e)}")

# tempos_db = Database()
# resultado = tempos_db.get_precificacao(None,True)
# print(resultado)
