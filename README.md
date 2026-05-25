# Desafio NoSQL - Integração MongoDB & Redis (Cache-Aside)

Este projeto apresenta o desenvolvimento de um script em Python que se conecta de forma simultânea a um banco de dados relacional NoSQL orientado a documentos (**MongoDB Atlas**) e a uma camada de armazenamento em memória (**Upstash Redis**). O objetivo principal é demonstrar operações de CRUD e a implementação prática de uma estratégia de cache de dados (*Cache-Aside*).

## 🚀 Tecnologias e Bibliotecas Utilizadas

* **Python 3.14+**
* **pymongo:** Driver oficial do MongoDB para Python.
* **redis:** Cliente Python oficial para comunicação com o Redis.
* **Upstash Redis / MongoDB Atlas:** Instâncias NoSQL gerenciadas na nuvem.

---

## 🛠️ Requisitos e Dependências

Antes de executar o script, certifique-se de instalar as dependências obrigatórias utilizando o gerenciador de pacotes `pip`:

```bash
pip install pymongo redis