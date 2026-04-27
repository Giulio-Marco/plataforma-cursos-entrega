# Plataforma de Cursos

Projeto em Flask com:
- usuarios
- categorias
- cursos
- modulos
- aulas
- matriculas
- progresso
- avaliacoes
- trilhas
- certificados
- planos
- assinaturas
- pagamentos

## Requisitos
- Python 3.10 ou superior

## Como instalar
1. Abra o terminal na pasta do projeto
2. Crie um ambiente virtual:
   python -m venv .venv

3. Ative o ambiente virtual no Windows:
   .venv\Scripts\activate

4. Instale as dependencias:
   pip install -r requirements.txt

## Como rodar
1. Execute:
   python main.py

2. Abra no navegador:
   http://127.0.0.1:5000

## Como carregar exemplos
Se quiser popular o sistema com dados de exemplo, abra:
http://127.0.0.1:5000/popular-demo

## Usuarios de exemplo
- Professor Daniel:
  email: daniel@cursos.com
  senha: 123456

- Ana Souza:
  email: ana@cursos.com
  senha: 123456

- Bruno Martins:
  email: bruno@cursos.com
  senha: 123456

- Carlos Lima:
  email: carlos@cursos.com
  senha: 123456

- Marina Alves:
  email: marina@cursos.com
  senha: 123456

- Joao Pedro:
  email: joao@cursos.com
  senha: 123456

## Funcionalidades
- cadastro e login
- cadastro de categoria
- criacao de curso por instrutor
- criacao de modulos
- criacao de aulas
- matricula de alunos
- conclusao de aulas
- geracao de certificado
- avaliacao de cursos
- assinatura de planos

## Observacao importante
Se houver problema com banco antigo, apague o arquivo:
instance/plataforma.db

Depois rode novamente:
python main.py
