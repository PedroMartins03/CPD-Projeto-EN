import sys
import time
import random
import multiprocessing


# ============================================================
# GERAÇÃO DA GRELHA
# ============================================================

def generate_random_grid(rows, cols):

    # Lista que vai conter toda a grelha
    grid = []

    # Criar cada linha
    for row in range(rows):

        current_row = []

        # Criar cada coluna da linha
        for col in range(cols):

            # Escolhe aleatoriamente 0 ou 1
            value = random.randint(0, 1)

            current_row.append(value)

        # Adiciona a linha à grelha
        grid.append(current_row)

    return grid


# ============================================================
# CONTAGEM DE VIZINHOS
# ============================================================

def count_neighbors(grid, row, col):

    total_neighbors = 0

    total_rows = len(grid)
    total_cols = len(grid[0])

    # Percorrer as posições à volta da célula
    for row_offset in [-1, 0, 1]:

        for col_offset in [-1, 0, 1]:

            # Ignorar a própria célula
            if row_offset == 0 and col_offset == 0:
                continue

            # Calcular coordenadas do vizinho
            neighbor_row = row + row_offset
            neighbor_col = col + col_offset

            # Verificar se o vizinho não está fora da grid
            if (neighbor_row >= 0 and neighbor_row < total_rows and neighbor_col >= 0 and neighbor_col < total_cols):
                total_neighbors += grid[neighbor_row][neighbor_col]

    return total_neighbors


# ============================================================
# PRÓXIMA GERAÇÃO (SEQUENCIAL)
# ============================================================

def next_generation(grid):

    rows = len(grid)
    cols = len(grid[0])

    new_grid = []

    # Criar uma grelha vazia
    for row in range(rows):

        new_row = []

        for col in range(cols):
            new_row.append(0)

        new_grid.append(new_row)

    # Aplicar as regras do Game of Life
    for row in range(rows):

        for col in range(cols):

            current_cell = grid[row][col]

            alive_neighbors = count_neighbors(grid, row, col)

            # Célula viva
            if current_cell == 1:

                if alive_neighbors < 2:

                    new_grid[row][col] = 0

                elif alive_neighbors == 2 or alive_neighbors == 3:

                    new_grid[row][col] = 1

                else:

                    new_grid[row][col] = 0

            # Célula morta
            else:

                if alive_neighbors == 3:

                    new_grid[row][col] = 1

                else:

                    new_grid[row][col] = 0

    return new_grid


# ============================================================
# VERSÃO SEQUENCIAL
# ============================================================

def game_of_life_sequential(grid, generations):

    current_grid = []

    # Fazer cópia da grelha
    for row in grid:

        copied_row = []

        for value in row:

            copied_row.append(value)

        current_grid.append(copied_row)

    # Executar todas as gerações
    for generation in range(generations):

        current_grid = next_generation(current_grid)

    return current_grid


# ============================================================
# WORKER PARALELO
# ============================================================

def worker_task(data):

    grid = data[0]
    start_row = data[1]
    end_row = data[2]

    cols = len(grid[0])

    partial_result = []

    # Aplicar as regras do Game of Life
    for row in range(start_row, end_row):

        new_row = []

        for col in range(cols):

            current_cell = grid[row][col]

            alive_neighbors = count_neighbors(grid, row, col)

            if current_cell == 1:

                if alive_neighbors < 2:
                    new_row.append(0)

                elif alive_neighbors == 2 or alive_neighbors == 3:
                    new_row.append(1)

                else:
                    new_row.append(0)

            else:

                if alive_neighbors == 3:
                    new_row.append(1)

                else:
                    new_row.append(0)

        partial_result.append(new_row)

    return (start_row, partial_result)


# ============================================================
# VERSÃO PARALELA
# ============================================================

def game_of_life_parallel(grid, generations, workers):

    current_grid = []

    # Cópia da grelha
    for row in grid:

        copied_row = []

        for value in row:

            copied_row.append(value)

        current_grid.append(copied_row)

    total_rows = len(current_grid)

    for generation in range(generations):

        rows_per_worker = total_rows // workers

        tasks = []

        current_start = 0

        # Dividir linhas pelos workers
        for worker in range(workers):

            current_end = (current_start + rows_per_worker)

            # Último worker fica com o resto
            if worker == workers - 1:
                current_end = total_rows

            tasks.append((current_grid, current_start, current_end))

            current_start = current_end

        # Criar workers
        pool = multiprocessing.Pool(processes=workers)

        partial_results = pool.map(worker_task, tasks)

        pool.close()
        pool.join()

        # Ordenar resultados
        partial_results.sort(key=lambda result: result[0])

        next_grid = []

        # Juntar todas as partes
        for result in partial_results:
            block = result[1]

            for row in block:
                next_grid.append(row)

        current_grid = next_grid

    return current_grid


# ============================================================
# MAIN
# ============================================================

def main():

    if len(sys.argv) != 4:

        print("Uso:")

        print("python game_of_life.py 1000x1000 100 4")

        return

    grid_size = sys.argv[1]

    generations = int(sys.argv[2])

    workers = int(sys.argv[3])

    size_parts = grid_size.split("x")

    rows = int(size_parts[0])
    cols = int(size_parts[1])

    print("A gerar grelha...")

    random.seed(42)

    grid = generate_random_grid(rows, cols)

    print("\nVERSÃO SEQUENCIAL")

    start_time = time.perf_counter()

    sequential_result = (game_of_life_sequential(grid, generations))

    sequential_time = (time.perf_counter() - start_time)

    print(
        f"Tempo: {sequential_time:.3f} segundos"
    )

    print("\nVERSÃO PARALELA")

    start_time = time.perf_counter()

    parallel_result = (game_of_life_parallel(grid, generations, workers))

    parallel_time = (time.perf_counter() - start_time)

    print(
        f"Tempo: {parallel_time:.3f} segundos"
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