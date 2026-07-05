"""
Servidor fica responsável pela parte inicial da comunicação entre
cliente e servidor. A lógica dos primos e do Game of Life fica separada
em primos.py e game_of_life.py.
"""

import inspect
import json
import socket
import threading
import time

# Configuração inicial do servidor.
# O servidor fica à escuta em todas as ‘interfaces’ da máquina, na porta 8000.
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000
BUFFER_SIZE = 4096
DEFAULT_WORKERS = 4

# Aqui fazemos a ligação às funções que vão ser implementadas noutros ficheiros.
from primos import find_max_prime_parallel, find_max_prime_sequential, is_prime

def find_max_prime_par(timeout):
    return f"Procura paralela em {timeout} segundos com {DEFAULT_WORKERS} workers...",find_max_prime_parallel(timeout, DEFAULT_WORKERS)
def find_max_prime_seq(timeout):
    return f"Procura sequencial em {timeout} segundos...",find_max_prime_sequential(timeout)
def prime_is_prime(n):
    return is_prime(n)


from game_of_life import game_of_life_parallel, game_of_life_sequential

def game_of_life_seq(grid, generations):

    inicio = time.perf_counter()

    game_of_life_sequential(grid, generations)

    fim = time.perf_counter()

    return {
        "tempo": fim - inicio
    }


def game_of_life_par(grid, generations, workers):

    inicio = time.perf_counter()

    game_of_life_parallel(grid, generations, workers)

    fim = time.perf_counter()

    return {
        "tempo": fim - inicio,
        "workers": workers
    }


def list_methods():
    """Devolve a lista de operações disponíveis no servidor."""
    methods = []

    for name, func in OPERACOES.items():
        signature = inspect.signature(func)
        params = list(signature.parameters.keys())
        methods.append({
            "nome": name,
            "parametros": params,
            "descricao": inspect.getdoc(func) or ""
        })

    return methods

# Operações que o cliente pode pedir ao servidor.
# Estes nomes têm de ser iguais aos nomes enviados no campo "method" do JSON.
OPERACOES = {
    "find_max_prime_parallel": find_max_prime_par,
    "find_max_prime_sequential": find_max_prime_seq,
    "is_prime": is_prime,
    "game_of_life_parallel": game_of_life_par,
    "game_of_life_sequential": game_of_life_seq,
    "list_methods": list_methods,
}

def receber_json(conn):
    """Recebe a mensagem enviada pelo cliente e converte-a para JSON."""
    dados = b""

    while True:
        parte = conn.recv(BUFFER_SIZE)
        if not parte:
            break

        dados += parte

        try:
            return json.loads(dados.decode("utf-8").strip())
        except json.JSONDecodeError:
            # Se o JSON ainda não estiver completo, continuamos a receber dados.
            continue

    if not dados:
        raise ValueError("Pedido vazio.")

    return json.loads(dados.decode("utf-8").strip())

def enviar_json(conn, resposta):
    """Converte a resposta para JSON e envia-a de volta ao cliente."""
    mensagem = json.dumps(resposta).encode("utf-8")
    conn.sendall(mensagem)

def processar_pedido(pedido):
    """Confirma se o pedido é válido e chama a operação pedida."""
    if not isinstance(pedido, dict):
        return {"error": "Pedido invalido."}

    method = pedido.get("method")
    params = pedido.get("params", {})

    if not isinstance(method, str):
        return {"error": "Campo method invalido."}

    if not isinstance(params, dict):
        return {"error": "Campo params deve ser um objeto JSON."}

    funcao = OPERACOES.get(method)
    if funcao is None:
        return {"error": "Metodo nao encontrado."}

    try:
        # Os parâmetros vêm num dicionário e são passados à função pelo nome.
        resultado = funcao(**params)
        return {"result": resultado}
    except Exception as erro:
        return {"error": str(erro)}

def tratar_cliente(conn, addr):
    """Recebe, processa e responde a um pedido de um cliente."""
    print("Cliente ligado:", addr)

    with conn:
        try:
            # Primeiro recebemos o pedido que chegou pelo socket.
            pedido = receber_json(conn)
            print("Pedido recebido:", pedido)

            # Depois encaminhamos o pedido para a função certa.
            resposta = processar_pedido(pedido)
            print("Resposta enviada:", resposta)

            # Por fim enviamos a resposta, também em JSON.
            enviar_json(conn, resposta)
        except Exception as erro:
            enviar_json(conn, {"error": str(erro)})

    print("Cliente desligado:", addr)

def iniciar_servidor():
    """Prepara o socket do servidor e fica à espera de clientes."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen()

        print(f"Servidor RPC a escuta em {SERVER_HOST}:{SERVER_PORT}")

        while True:
            # O servidor fica sempre à espera de novas ligações.
            conn, addr = server_socket.accept()

            # Cada cliente fica numa thread própria, como nos laboratórios.
            thread = threading.Thread(target=tratar_cliente, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    iniciar_servidor()