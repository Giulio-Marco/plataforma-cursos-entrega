# Plataforma de Cursos

Projeto em Flask para gerenciamento de uma plataforma de cursos online.

## Funcionalidades
- cadastro e login de usuarios
- cadastro de categorias
- criacao de curso por instrutor
- criacao de modulos
- criacao de aulas
- matricula de alunos
- conclusao de aulas
- geracao de certificado
- avaliacao de cursos
- assinatura de planos

## Links
- Aplicacao online: https://plataforma-cursos-entrega.onrender.com
- Carregar dados de exemplo: https://plataforma-cursos-entrega.onrender.com/popular-demo
- Repositorio no GitHub: https://github.com/Giulio-Marco/plataforma-cursos-entrega

## Requisitos
- Python 3.10 ou superior

## Como instalar
1. Abra o terminal na pasta do projeto
2. Crie um ambiente virtual:
   `python -m venv .venv`

3. Ative o ambiente virtual no Windows:
   `.venv\Scripts\activate`

4. Instale as dependencias:
   `pip install -r requirements.txt`

## Como rodar localmente
1. Execute:
   `python main.py`

2. Abra no navegador:
   `http://127.0.0.1:5000`

## Como carregar exemplos
Se quiser popular o sistema com dados de exemplo localmente, abra:
`http://127.0.0.1:5000/popular-demo`

Se estiver usando a versao online, abra:
`https://plataforma-cursos-entrega.onrender.com/popular-demo`

## Usuarios de exemplo
- Professor Daniel
  email: `daniel@cursos.com`
  senha: `123456`

- Ana Souza
  email: `ana@cursos.com`
  senha: `123456`

- Bruno Martins
  email: `bruno@cursos.com`
  senha: `123456`

- Carlos Lima
  email: `carlos@cursos.com`
  senha: `123456`

- Marina Alves
  email: `marina@cursos.com`
  senha: `123456`

- Joao Pedro
  email: `joao@cursos.com`
  senha: `123456`

## Observacao importante
Se os usuarios de exemplo nao estiverem funcionando na aplicacao online, acesse primeiro:
`https://plataforma-cursos-entrega.onrender.com/popular-demo`

Como o projeto esta usando SQLite no Render, os dados de demonstracao podem precisar ser carregados novamente em alguns casos.

## Banco local
Se houver problema com banco antigo, apague o arquivo:
`instance/plataforma.db`

Depois rode novamente:
`python main.py`
