import multiprocessing
import time

# Função dada pelo professor
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    divisor = 5
    while divisor * divisor <= n:
        if n % divisor == 0 or n % (divisor + 2) == 0:
            return False
        divisor += 6
    return True

def find_max_prime_sequential(timeout: int) -> int:
    if timeout <= 0: #validação apenas contra erros
        raise ValueError("O timeout deve ser maior que 0")
    start_time = time.perf_counter() #timer do python sem erros
    max_prime_found = 2
    current = 3
    #Conta enquanto o tempo for menor que o timeout recebido
    while (time.perf_counter() - start_time) < timeout:
        if is_prime(current):
            max_prime_found = current
        current += 2
    return max_prime_found

def worker_prime_search(start_num, step, timeout, start_time, result_queue):
    max_p = -1
    current = start_num

    while (time.perf_counter() - start_time) < timeout:
        if is_prime(current):
            max_p = current
        current += step

    # Quando sai do ciclo (tempo acabou), coloca o maior que encontrou na Queue
    result_queue.put(max_p)


def find_max_prime_parallel(timeout: int, workers: int) -> int:
    if timeout <= 1: #fazer com que os workers tenham tempo de procurar
        raise ValueError("O timeout deve ser maior que 1")

    # A Queue serve para os workers enviarem o resultado de volta para o processo principal
    result_queue = multiprocessing.Queue()
    processes = []

    start_time = time.perf_counter()

    # Criar e arrancar os processos
    for i in range(workers):
        # Começamos no 3. Cada worker vai arrancar num número diferente.
        start_num = 3 + (i * 2)
        # O step é o dobro dos workers para que ignorem os números pares
        step = workers * 2

        p = multiprocessing.Process(target=worker_prime_search,
                                    args=(start_num, step, timeout, start_time, result_queue))
        processes.append(p)
        p.start()

    # Resultados
    max_primes = []
    for _ in range(workers): #não precisa de "i", pois apenas vai buscar os resultados dos workers
        # O .get() bloqueia até haver um valor na Queue,
        # para que os workers tenham tempo de dar todos os valores, congelando e esperar invés de parar o programa
        max_primes.append(result_queue.get())

    # Fazer com que todos os processos fecham de maneira certa, sem fechar prematuramente
    for p in processes:
        p.join()

    # Devolver o maior primo de entre todos os encontrados pelos workers
    return max(max_primes)

def main():
    print("\nVERSÃO SEQUENCIAL")

    start_time = time.perf_counter()

    sequential_result = (find_max_prime_sequential(2))

    sequential_time = (time.perf_counter() - start_time)

    print(
        f"Tempo: {sequential_time:.3f} segundos\nMáximo Sequencial: {sequential_result}"
    )

    print("\nVERSÃO PARALELA")

    start_time = time.perf_counter()

    parallel_result = (find_max_prime_parallel(2,4))

    parallel_time = (time.perf_counter() - start_time)

    print(
        f"Tempo: {parallel_time:.3f} segundos\nMáximo Paralelo: {parallel_result}"
    )

    print("\nVALIDAÇÃO")

    if sequential_result == parallel_result:

        print("Os resultados são iguais.")

    else:

        print("Os resultados são diferentes.")

    speedup = (sequential_time / parallel_time)

    print(f"\nSpeedup: {speedup:.2f}x")


if __name__ == "__main__":
    main()