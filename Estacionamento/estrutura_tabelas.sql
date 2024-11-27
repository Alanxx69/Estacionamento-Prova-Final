CREATE TABLE cliente (
    id SERIAL PRIMARY KEY,
    cpf VARCHAR(11) UNIQUE NOT NULL,
    nome_completo VARCHAR(100) NOT NULL
);

CREATE TABLE cliente_veiculo (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    marca_veiculo VARCHAR(50),
    modelo_veiculo VARCHAR(50),
    placa VARCHAR(7) UNIQUE NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES cliente(id)
);
CREATE TABLE vagas (
    id SERIAL PRIMARY KEY,
    numero_vaga VARCHAR(10) NOT NULL,
    status VARCHAR(20) DEFAULT 'disponivel'  -- disponível, ocupada, reservada
)
CREATE TABLE estacionamento (
    id SERIAL PRIMARY KEY,
    vaga_id INTEGER NOT NULL,
    cliente_veiculo_id INTEGER NOT NULL,
    data_hora_entrada TIMESTAMP NOT NULL,
    data_hora_saida TIMESTAMP,
    tempo_permanencia VARCHAR(25),  -- Diferença entre data_hora_saida e data_hora_entrada
    status VARCHAR(20),  -- ativo, concluido
    FOREIGN KEY (vaga_id) REFERENCES vagas(id) ON DELETE CASCADE,
    FOREIGN KEY (cliente_veiculo_id) REFERENCES cliente_veiculo(id)
);
