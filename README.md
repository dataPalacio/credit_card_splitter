# 💸 Controle de Gastos Pessoais

Este é um aplicativo web desenvolvido com [Streamlit](https://streamlit.io/) para registrar, visualizar, editar e excluir seus próprios gastos de forma simples e intuitiva.

## ✅ Funcionalidades
- Registro de gastos com data, valor, categoria, cartão e parcelas
- Definição de limite mensal
- Filtro opcional por mês
- Edição e exclusão de registros
- Cálculo de total gasto e limite restante

## 🚀 Como Executar Localmente

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o app:
```bash
streamlit run app/app_pessoal.py
```

## ☁️ Como Fazer Deploy no Streamlit Cloud

1. Faça login em https://streamlit.io/cloud
2. Clique em **"New app"**
3. Conecte seu repositório GitHub
4. Escolha o arquivo `app/app_pessoal.py`
5. Clique em **Deploy**

Pronto! O app será hospedado com um link como:

```
https://<seu-usuario>-<repo>.streamlit.app
```

## 📁 Estrutura recomendada do projeto

```
meu-projeto/
├── app/
│   └── app_pessoal.py
├── db/
│   └── gastos.db  ← (pode ser ignorado no .gitignore se quiser um banco novo)
├── requirements.txt
└── README.md
```

## 📌 Observações

- O banco de dados `gastos.db` é um arquivo local persistido no servidor do Streamlit Cloud.
- Para múltiplos usuários ou acessos simultâneos, considere usar um banco remoto como PostgreSQL ou Firebase.

---

Desenvolvido por ❤️ com Streamlit
