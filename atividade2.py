import json
import redis
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from redis.exceptions import ConnectionError, AuthenticationError

MONGO_URI = "mongodb+srv://dbUser:dbUserPassword@cluster0.3zbk4z8.mongodb.net/?appName=Cluster0"
REDIS_URL = "rediss://default:gQAAAAAAAhTSAAIgcDI3ODUyMzI0ZjQ1NGI0ZGE3ODBkZWRjNWM2MTM1MjI3NA@fluent-shiner-136402.upstash.io:6379"

def conectar_mongodb():
    try:
        print("Conectando ao MongoDB Atlas...")
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("Conectado ao MongoDB com sucesso!")
        db = client["desafio_nosql"]
        return db["produtos"]
    except ConnectionFailure:
        print("Erro: Não foi possível conectar ao servidor do MongoDB.")
        return None
    except OperationFailure as e:
        print(f"Erro de Autenticação ou Operação no MongoDB: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return None

def inserir_produtos_iniciais(colecao):
    lista_produtos = [
        {"nome": "alfa0ce", "preco": 9.50, "categoria": "hortifruti"},
        {"nome": "sucrilhos", "preco": 19.50, "categoria": "cereais"},
        {"nome": "halls", "preco": 2.50, "categoria": "doces"}
    ]
    try:
        print("\nInserindo produtos no MongoDB...")
        resultado = colecao.insert_many(lista_produtos)
        print(f"Sucesso! {len(resultado.inserted_ids)} produtos foram inseridos.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado na inserção: {e}")

def consultar_produtos_caros(colecao):
    try:
        print("\nBuscando produtos com preço maior que 10...")
        filtro = {"preco": {"$gt": 10.00}}
        produtos = colecao.find(filtro)
        encontrou = False
        for produto in produtos:
            encontrou = True
            print(f"- Nome: {produto['nome']} | Preço: R${produto['preco']:.2f} | Categoria: {produto['categoria']}")
        if not encontrou:
            print("Nenhum produto com preço maior que 10 foi encontrado.")
    except Exception as e:
        print(f"Erro ao consultar os produtos: {e}")

def alterar_preco_produto(colecao, nome, novo_preco):
    try:
        print(f"\nTentando atualizar o preço de '{nome}' para R${novo_preco:.2f}...")
        filtro = {"nome": nome}
        novos_valores = {"$set": {"preco": novo_preco}}
        resultado = colecao.update_one(filtro, novos_valores)

        if resultado.matched_count > 0:
            if resultado.modified_count > 0:
                print(f"Sucesso! O preço do produto '{nome}' foi updated.")
            else:
                print(f"O produto '{nome}' foi encontrado, mas o preço já era R${novo_preco:.2f}.")
        else:
            print(f"Aviso: Nenhum produto com o nome '{nome}' foi encontrado.")
    except Exception as e:
        print(f"Erro ao atualizar o produto: {e}")

def deletar_produto_categoria(colecao, categoria_alvo):
    try:
        print(f"\nTentando remover produtos da categoria: '{categoria_alvo}'...")
        filtro = {"categoria": categoria_alvo}

        produto_a_deletar = colecao.find_one(filtro)
        if produto_a_deletar is None:
            print(f"Aviso: Nenhum produto encontrado na categoria '{categoria_alvo}'.")
            return

        nome_deletado = produto_a_deletar["nome"]
        resultado = colecao.delete_one({"_id": produto_a_deletar["_id"]})
        
        if resultado.deleted_count > 0:
            print(f"Sucesso! O produto '{nome_deletado}' da categoria '{categoria_alvo}' foi removido.")
    except Exception as e:
        print(f"Erro ao remover o produto: {e}")

def conectar_redis():
    try:
        print("\nConectando ao Redis (Upstash)...")
        r = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=15)
        r.ping()
        print("Conectado ao Redis com sucesso!")
        return r
    except AuthenticationError:
        print("Erro de Autenticação no Redis.")
        return None
    except ConnectionError:
        print("Erro: Não foi possível conectar ao servidor do Redis.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao conectar no Redis: {e}")
        return None

def armazenar_mensagem_boas_vindas(redis_client):
    try:
        chave = "mensagem:inicio"
        valor = "Bem-vindo ao desafio NoSQL! Camada de cache ativada."
        print(f"Armazenando chave '{chave}' no Redis...")
        redis_client.set(chave, valor)
        print("Mensagem armazenada com sucesso!")
    except Exception as e:
        print(f"Erro ao operar no Redis: {e}")

def armazenar_usuario_hash(redis_client, id_usuario, nome, email):
    try:
        chave_usuario = f"usuario:{id_usuario}"
        dados_usuario = {"nome": nome, "email": email}
        print(f"\n[Redis] Salvando Hash para a chave '{chave_usuario}'...")
        redis_client.hset(chave_usuario, mapping=dados_usuario)
        print("Usuário salvo em estrutura Hash com sucesso!")
        usuario_recuperado = redis_client.hgetall(chave_usuario)
        print(f"Dados recuperados do Hash: {usuario_recuperado}")
    except Exception as e:
        print(f"Erro ao operar Hash no Redis: {e}")

def registrar_log_acesso(redis_client, acao):
    try:
        chave_logs = "logs:acesso"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entrada_log = f"[{timestamp}] - Ação: {acao}"
        redis_client.rpush(chave_logs, entrada_log)
    except Exception as e:
        print(f"Erro ao registrar log no Redis: {e}")

def exibir_todos_logs(redis_client):
    try:
        chave_logs = "logs:acesso"
        print(f"\n[Redis] Recuperando todos os elementos da lista '{chave_logs}':")
        todos_logs = redis_client.lrange(chave_logs, 0, -1)
        if todos_logs:
            for log in todos_logs:
                print(f"  {log}")
        else:
            print("A lista de logs está vazia.")
    except Exception as e:
        print(f"Erro ao recuperar logs do Redis: {e}")

def buscar_produto_com_cache(colecao_mongo, cliente_redis, nome_produto):
    chave_cache = f"produto:{nome_produto}"
    try:
        print(f"\n[Redis] Verificando se '{nome_produto}' está no cache...")
        produto_em_cache = cliente_redis.get(chave_cache)
        
        if produto_em_cache:
            print(f"⚡ CACHE HIT! '{nome_produto}' encontrado no Redis.")
            registrar_log_acesso(cliente_redis, f"Busca de '{nome_produto}' (CACHE HIT)")
            return json.loads(produto_em_cache)
            
        print(f"🐢 CACHE MISS! '{nome_produto}' não está no Redis. Buscando no MongoDB...")
        produto_mongo = colecao_mongo.find_one({"nome": nome_produto})
        
        if produto_mongo:
            produto_mongo["_id"] = str(produto_mongo["_id"])
            produto_json = json.dumps(produto_mongo)
            cliente_redis.set(chave_cache, produto_json, ex=60)
            print(f"💾 Cópia de '{nome_produto}' guardada no Redis por 60 segundos.")
            registrar_log_acesso(cliente_redis, f"Busca de '{nome_produto}' (CACHE MISS)")
            return produto_mongo
        else:
            print(f"❌ O produto '{nome_produto}' não existe.")
            registrar_log_acesso(cliente_redis, f"Busca de '{nome_produto}' (NÃO ENCONTRADO)")
            return None
    except Exception as e:
        print(f"Erro ao gerenciar o cache: {e}")
        return None


if __name__ == "__main__":
    colecao_produtos = conectar_mongodb()
    cliente_redis = conectar_redis()
    
    if colecao_produtos is not None and cliente_redis is not None:
        armazenar_mensagem_boas_vindas(cliente_redis)
        
        armazenar_usuario_hash(cliente_redis, id_usuario="1", nome="Joás", email="joas@email.com")
        
        print("\n--- CASO INTEGRADO (TESTE DE CACHE) ---")
        p1 = buscar_produto_com_cache(colecao_produtos, cliente_redis, "sucrilhos")
        p2 = buscar_produto_com_cache(colecao_produtos, cliente_redis, "sucrilhos")
        
        exibir_todos_logs(cliente_redis)