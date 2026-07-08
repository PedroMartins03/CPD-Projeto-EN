import unittest
import threading
import socket

# Importar todas as funções desenvolvidas
from primos import is_prime, find_max_prime_sequential, find_max_prime_parallel
from game_of_life import (
    generate_random_grid, count_neighbors, next_generation,
    game_of_life_sequential, game_of_life_parallel
)
import servidor
import cliente


class TestPrimos(unittest.TestCase):
    """Testes para o módulo primos.py"""

    def test_is_prime(self):
        self.assertTrue(is_prime(2))
        self.assertTrue(is_prime(17))
        self.assertFalse(is_prime(4))
        self.assertFalse(is_prime(15))

    def test_find_max_prime_sequential(self):
        # Testa com 2 segundos de timeout
        resultado = find_max_prime_sequential(2)
        self.assertTrue(resultado > 2)
        self.assertTrue(is_prime(resultado))

    def test_find_max_prime_parallel(self):
        # Testa a versão paralela com 2 segundos e 4 workers
        resultado = find_max_prime_parallel(2, 4)
        self.assertTrue(resultado > 2)
        self.assertTrue(is_prime(resultado))


class TestGameOfLife(unittest.TestCase):
    """Testes para o módulo game_of_life.py"""

    def setUp(self):
        # Grelha estática pequena para testes apenas
        self.grid_inicial = [
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        self.grid_esperada_gen1 = [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ]

    def test_generate_random_grid(self):
        grid = generate_random_grid(5, 10)
        self.assertEqual(len(grid), 5)
        self.assertEqual(len(grid[0]), 10)

    def test_count_neighbors(self):
        # A célula do meio tem 2 vizinhos vivos acima e abaixo
        vizinhos = count_neighbors(self.grid_inicial, 2, 2)
        self.assertEqual(vizinhos, 2)

    def test_next_generation(self):
        grid_result = next_generation(self.grid_inicial)
        self.assertEqual(grid_result, self.grid_esperada_gen1)

    def test_game_of_life_sequential(self):
        grid_result = game_of_life_sequential(self.grid_inicial, 1)
        self.assertEqual(grid_result, self.grid_esperada_gen1)

    def test_game_of_life_parallel(self):
        grid_result = game_of_life_parallel(self.grid_inicial, 1, 2)
        self.assertEqual(grid_result, self.grid_esperada_gen1)


class TestRPC(unittest.TestCase):
    """Testes para os módulos servidor.py e cliente.py"""

    def test_servidor_processar_pedido(self):
        # Verificar pedidos válidos
        pedido_valido = {"method": "list_methods", "params": {}}
        resposta_valida = servidor.processar_pedido(pedido_valido)

        self.assertIn("result", resposta_valida)
        # Verifica se devolve as 6 operações realizadas
        self.assertEqual(len(resposta_valida["result"]), 6)

        pedido_invalido = {"method": "metodo_inexistente", "params": {}}
        resposta_invalida = servidor.processar_pedido(pedido_invalido)

        self.assertIn("error", resposta_invalida)

    def test_cliente_servidor(self):

        def aceitar_cliente(server_sock):
            conn, addr = server_sock.accept()
            servidor.tratar_cliente(conn, addr)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(("127.0.0.1", 0))
            server_socket.listen(1)

            cliente.SERVER_PORT = server_socket.getsockname()[1]
            cliente.SERVER_HOST = "127.0.0.1"

            thread = threading.Thread(
                target=aceitar_cliente,
                args=(server_socket,)
            )
            thread.start()

            resposta = cliente.enviar_pedido("list_methods", {})
            thread.join()

        self.assertIn("result", resposta)


if __name__ == "__main__":
    unittest.main()