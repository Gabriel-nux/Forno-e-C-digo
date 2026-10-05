-- Dinheiro é sempre centavo inteiro (INTEGER), nunca NUMERIC nem float.

CREATE TABLE administradores (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome            VARCHAR(100) NOT NULL CHECK (length(btrim(nome)) > 0),
    -- o CHECK obriga o e-mail a ser minúsculo, senão dava pra furar o UNIQUE com maiúsculas
    email           VARCHAR(254) NOT NULL UNIQUE
                    CHECK (email = lower(email) AND position('@' IN email) > 1),
    senha_hash      VARCHAR(255) NOT NULL,
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now(),
    ultimo_login_em TIMESTAMPTZ
);

CREATE TABLE clientes (
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(100) NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    senha_hash      VARCHAR(255) NOT NULL,
    telefone        VARCHAR(20),
    endereco_padrao TEXT
);

CREATE TABLE categorias (
    id     SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL UNIQUE CHECK (codigo ~ '^[a-z]+$'),
    nome   VARCHAR(60) NOT NULL
);

CREATE TABLE tamanhos (
    id     SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE CHECK (codigo ~ '^[a-z]+$'),
    nome   VARCHAR(30) NOT NULL,
    ordem  SMALLINT NOT NULL UNIQUE
);

CREATE TABLE produtos (
    id            INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    slug          VARCHAR(80) NOT NULL UNIQUE CHECK (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
    nome          VARCHAR(100) NOT NULL CHECK (length(btrim(nome)) > 0),
    descricao     TEXT NOT NULL DEFAULT '',
    categoria_id  SMALLINT NOT NULL REFERENCES categorias (id),
    imagem_chave  VARCHAR(60),
    disponivel    BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX produtos_categoria_idx ON produtos (categoria_id);

-- um preço por produto e tamanho; nem todo sabor precisa existir em todo tamanho
CREATE TABLE produto_precos (
    produto_id     INTEGER  NOT NULL REFERENCES produtos (id) ON DELETE CASCADE,
    tamanho_id     SMALLINT NOT NULL REFERENCES tamanhos (id),
    preco_centavos INTEGER  NOT NULL CHECK (preco_centavos > 0),
    PRIMARY KEY (produto_id, tamanho_id)
);
CREATE INDEX produto_precos_tamanho_idx ON produto_precos (tamanho_id);

CREATE TABLE pedidos (
    id               INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id       INTEGER REFERENCES clientes (id) ON DELETE SET NULL,
    status           VARCHAR(20) NOT NULL DEFAULT 'pendente'
                     CHECK (status IN ('pendente', 'confirmado', 'em_preparo', 'saiu_para_entrega', 'entregue', 'cancelado')),
    endereco_entrega TEXT NOT NULL,
    observacoes      TEXT,
    total_centavos   INTEGER NOT NULL CHECK (total_centavos >= 0),
    criado_em        TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX pedidos_status_criado_idx ON pedidos (status, criado_em DESC);
CREATE INDEX pedidos_cliente_idx ON pedidos (cliente_id);

-- O item guarda uma cópia do nome e do preço da hora da compra: mexer no cardápio não reescreve pedido antigo.
CREATE TABLE itens_pedido (
    id                      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pedido_id               INTEGER  NOT NULL REFERENCES pedidos (id) ON DELETE CASCADE,
    tipo                    VARCHAR(10) NOT NULL CHECK (tipo IN ('inteira', 'meio')),
    produto_id              INTEGER  NOT NULL REFERENCES produtos (id),
    produto_metade_id       INTEGER  REFERENCES produtos (id),
    tamanho_id              SMALLINT NOT NULL REFERENCES tamanhos (id),
    nome_snapshot           VARCHAR(220) NOT NULL,
    quantidade              INTEGER  NOT NULL CHECK (quantidade > 0),
    preco_unitario_centavos INTEGER  NOT NULL CHECK (preco_unitario_centavos > 0),
    observacoes             TEXT,
    CONSTRAINT itens_pedido_tipo_coerente CHECK (
        (tipo = 'inteira' AND produto_metade_id IS NULL)
        OR (tipo = 'meio' AND produto_metade_id IS NOT NULL AND produto_metade_id <> produto_id)
    )
);
CREATE INDEX itens_pedido_pedido_idx ON itens_pedido (pedido_id);
CREATE INDEX itens_pedido_produto_idx ON itens_pedido (produto_id);
