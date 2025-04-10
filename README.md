# 💳 credit_card_splitter

Sistema de controle e divisão de despesas de faturas de cartão de crédito compartilhadas, com interface em **Streamlit** e persistência em **SQLite**.

---

## 🚀 Como executar o projeto

### 1. 📦 Clone o repositório

```bash
git clone https://github.com/seu-usuario/credit_card_splitter.git
cd credit_card_splitter
```

### 2. 🐍 Crie e ative um ambiente virtual (opcional, mas recomendado)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

### 3. 📥 Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. 🛠️ Inicialize o banco de dados (cria as tabelas vazias)

```bash
python data/seed_db.py
```

> Isso criará o arquivo `data/database.db` com as tabelas `pessoas`, `cartoes` e `compras`.

### 5. 💻 Execute a aplicação Streamlit

```bash
streamlit run app/app.py
```

O app abrirá automaticamente no navegador em:
👉 [http://localhost:8501](http://localhost:8501)

---

## 📂 Estrutura de pastas

```
credit_card_splitter/
├── app/            # Interface gráfica (Streamlit)
│   └── app.py
├── core/           # Lógica de divisão de despesas
│   └── calculator.py
├── db/             # Estrutura e conexão com banco SQLite
│   ├── database.py
│   └── models.py
├── data/           # Script de inicialização do banco
│   └── seed_db.py
├── data/database.db # Arquivo do banco SQLite (gerado após inicialização)
├── requirements.txt # Dependências do projeto
└── README.md        # Documentação do projeto
```

---

## ✅ Tecnologias utilizadas

- [Python 3.10+](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [SQLite (via sqlite3)](https://www.sqlite.org/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)

---

## 📌 Autor

Desenvolvido por [Gustavo](https://github.com/dataPalacio) com foco em boas práticas de engenharia de software, modularização e interface amigável para uso pessoal e compartilhado.
