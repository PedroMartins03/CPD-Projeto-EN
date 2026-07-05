"""
Cliente permite ao utilizador escolher uma operação, enviar o pedido
ao servidor em JSON e mostrar a resposta recebida. Serve de base
para testar as funções que vão ser ligadas ao servidor.
"""

import json
import socket

# Endereço e porta onde o servidor está à escuta.
# Como o teste é local, o cliente liga-se ao localhost.
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000
BUFFER_SIZE = 4096

def receber_json(sock):
    """Recebe a resposta do servidor e converte-a para JSON."""
    dados = b""

    while True:
        parte = sock.recv(BUFFER_SIZE)
        if not parte:
            break

        dados += parte

        try:
            return json.loads(dados.decode("utf-8").strip())
        except json.JSONDecodeError:
            # Se a resposta ainda não estiver completa, continuamos a receber.
            continue

    if not dados:
        raise ValueError("Resposta vazia do servidor.")

    return json.loads(dados.decode("utf-8").strip())

def enviar_pedido(method, params=None):
    """Monta um pedido RPC, envia-o ao servidor e devolve a resposta."""
    if params is None:
        params = {}

    pedido = {
        "method": method,
        "params": params
    }

    # Aqui o cliente cria o socket e faz a ligação ao servidor.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_HOST, SERVER_PORT))

        # O pedido é convertido para JSON e enviado em bytes.
        mensagem = json.dumps(pedido).encode("utf-8")
        client_socket.sendall(mensagem)

        # Depois o cliente fica à espera da resposta do servidor.
        return receber_json(client_socket)

def mostrar_resposta(resposta):
    """Mostra no ecrã o resultado ou o erro recebido."""
    if "result" in resposta:
        print("Resultado:")
        print(resposta["result"])
    elif "error" in resposta:
        print("Erro:")
        print(resposta["error"])
    else:
        print("Resposta invalida:")
        print(resposta)

def ler_inteiro(mensagem):
    """Lê um número inteiro introduzido pelo utilizador."""
    return int(input(mensagem).strip())

def menu():
    """Menu simples para testar as operações disponíveis no servidor."""
    while True:
        print("\n=== Cliente RPC ===")
        print("1. Listar metodos")
        print("2. Verificar primo")
        print("3. Procurar maior primo")
        print("4. Executar Game of Life")
        print("M. Pedido manual")
        print("0. Sair")

        opcao = input("Opcao: ").strip().lower()

        try:
            if opcao == "0":
                print("A terminar cliente.")
                break

            elif opcao == "1":
                resposta = enviar_pedido("list_methods", {})
                mostrar_resposta(resposta)

            elif opcao == "2":
                n = ler_inteiro("Numero: ")
                resposta = enviar_pedido("is_prime", {"n": n})
                mostrar_resposta(resposta)

            elif opcao == "3":
                timeout = ler_inteiro("Timeout em segundos: ")
                resposta_seq = enviar_pedido("find_max_prime_sequential", {"timeout": timeout})
                mostrar_resposta(resposta_seq)
                resposta_par = enviar_pedido("find_max_prime_parallel", {"timeout": timeout})
                mostrar_resposta(resposta_par)

            elif opcao == "4":
                print("Introduza a grelha em JSON. Exemplo: [[0,1,0],[1,1,1],[0,1,0]]")
                grid = json.loads(input("Grelha: ").strip())
                generations = ler_inteiro("Geracoes: ")
                resposta_seq = enviar_pedido(
                    "game_of_life_sequential",
                    {"grid": grid, "generations": generations}
                )
                mostrar_resposta(resposta_seq)
                resposta_par = enviar_pedido(
                    "game_of_life_parallel",
                    {"grid": grid, "generations": generations}
                )
                mostrar_resposta(resposta_par)

            elif opcao == "m":
                # Esta opção fica preparada para testar futuras funções do grupo.
                method = input("Nome do metodo: ").strip()
                print("Parametros em JSON. Exemplo: {\"timeout\": 5}")
                texto_params = input("Params: ").strip()

                if texto_params:
                    params = json.loads(texto_params)
                else:
                    params = {}

                resposta = enviar_pedido(method, params)
                mostrar_resposta(resposta)

            else:
                print("Opcao invalida.")

        except ConnectionRefusedError:
            print("Erro: nao foi possivel ligar ao servidor.")
        except ValueError as erro:
            print("Erro nos dados introduzidos:", erro)
        except json.JSONDecodeError:
            print("Erro: os parametros devem estar em formato JSON.")
        except Exception as erro:
            print("Erro:", erro)

if __name__ == "__main__":
    menu()