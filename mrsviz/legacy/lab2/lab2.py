# Индивидуальная лабораторная работа 2 по дисциплине МРЗвИС вариант 1
# Выполнена студентом группы 221702 БГУИР  Кветко Екатерины Дмитриевны
# Файл начала программы, создающий модель двунаправленной ассотиативной памяти и сохраняющий результат выполнения программы

# Использованные источники:
# Формальные модели обработки информации и параллельные модели решения задач. Практикум: учебно-методическое пособие / В.П.Ивашенко. – Минск: БГУИР, 2020.

from PIL import Image
import random 
import math 
import copy 


def load_image_to_vector(file_path):
    try:
        img = Image.open(file_path).convert('L') 
        data = list(img.getdata())
        width, height = img.size
        
        vector = [1 if pixel_value < 128 else -1 for pixel_value in data]
        
        print(f"Загружено '{file_path}'. Размер: {width}x{height} ({len(vector)} элементов)")
        
        return vector, width, height 
        
    except FileNotFoundError:
        return None, None, None
    except Exception as e:
        print(f"Ошибка при обработке изображения '{file_path}': {e}")
        return None, None, None


def save_vector_as_image(vector, width, height, filename):
    try:
        pixel_data = []
        for val in vector:
            pixel_data.append(0 if val == 1 else 255)
        
        img = Image.new('L', (width, height))
        img.putdata(pixel_data)
        img.save(filename)
        print(f"Изображение сохранено: {filename}")
        
    except Exception as e:
        print(f"Ошибка при сохранении изображения '{filename}': {e}")


def introduce_noise(vector, noise_percentage):
    noisy_vector = list(vector)
    N = len(noisy_vector)
    
    num_corrupt = int(N * noise_percentage / 100)
    
    indices_to_corrupt = random.sample(range(N), num_corrupt)
    
    for i in indices_to_corrupt:
        noisy_vector[i] *= -1
        
    print(f"Введен шум: инвертировано {num_corrupt} пикселей ({noise_percentage}%)")
    return noisy_vector

def create_bipolar_code(M, seed_val=1):
    random.seed(seed_val)
    code = [random.choice([1, -1]) for _ in range(M)]
    return code

def tanh_threshold(x):
    return math.tanh(x)

def vector_matrix_multiply(vector, matrix):
    N = len(vector)
    M = len(matrix[0])
    result = [0] * M
    for j in range(M):
        sum_val = 0
        for i in range(N):
            sum_val += vector[i] * matrix[i][j]
        result[j] = sum_val
    return result

def outer_product(vector_a, vector_b):
    N = len(vector_a)
    M = len(vector_b)
    matrix = [[0] * M for _ in range(N)]
    for i in range(N):
        for j in range(M):
            matrix[i][j] = vector_a[i] * vector_b[j]
    return matrix

def matrix_add(matrix1, matrix2):
    rows = len(matrix1)
    cols = len(matrix1[0])
    result = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            result[i][j] = matrix1[i][j] + matrix2[i][j]
    return result

def count_errors(v1, v2):
    if len(v1) != len(v2): return -1
    return sum(1 for i in range(len(v1)) if v1[i] != v2[i])


class BidirectionalAssociativeMemory:
    
    def __init__(self, activation_func=tanh_threshold):
        self.weight_matrix = None
        self.weight_matrix_t = None
        self.activation_func = activation_func 

    def train(self, pattern_pairs):
        if not pattern_pairs: return
        N = len(pattern_pairs[0][0])
        M = len(pattern_pairs[0][1])
        self.weight_matrix = [[0] * M for _ in range(N)]
        for A, B in pattern_pairs:
            current_weight_matrix = outer_product(A, B)
            self.weight_matrix = matrix_add(self.weight_matrix, current_weight_matrix)
        self.weight_matrix_t = [[self.weight_matrix[i][j] for i in range(N)] for j in range(M)]

    # --- ИЗМЕНЕННЫЙ МЕТОД RECALL ---
    def recall(self, input_vector, max_iterations=100):
        if self.weight_matrix is None: raise ValueError("Модель не обучена.")
        rows_W = len(self.weight_matrix)
        cols_W = len(self.weight_matrix[0])
        A, B = None, None
        
        # 1. Инициализация A и B
        if len(input_vector) == rows_W:
            A = list(input_vector)
            B = [0] * cols_W 
        elif len(input_vector) == cols_W:
            B = list(input_vector)
            A = [0] * rows_W 
        else: raise ValueError("Длина входного вектора не соответствует ни A, ни B.")

        if all(x == 0 for x in A): A = [self.activation_func(x) for x in A]
        if all(x == 0 for x in B): B = [self.activation_func(x) for x in B]

        # Список для хранения промежуточных состояний A
        recalled_states_A = [copy.deepcopy(A)] # Сохраняем начальный зашумленный вектор A

        # 2. Итерационный процесс восстановления
        for iteration in range(max_iterations):
            A_prev = list(A)
            B_prev = list(B)
            
            # A -> B (Активация B)
            B_potential = vector_matrix_multiply(A, self.weight_matrix)
            B = [self.activation_func(x) for x in B_potential]
            
            # B -> A (Активация A)
            A_potential = vector_matrix_multiply(B, self.weight_matrix_t)
            A = [self.activation_func(x) for x in A_potential]
            
            # Сохраняем состояние A после полной итерации A->B->A
            recalled_states_A.append(copy.deepcopy(A))
            
            # Проверка сходимости
            if A == A_prev and B == B_prev: 
                print(f"Сходимость достигнута за {iteration + 1} итераций.")
                break
        else:
             print(f"Сходимость не достигнута за {max_iterations} итераций. Восстановление остановлено.")
                
        # Возвращаем список состояний A, и финальное состояние B
        return recalled_states_A, B
    # ------------------------------------


def run_example():
    
    print("выбор режима: 1 или 2")

    try:
        TRAINING_MODE = int(input())
    except ValueError:
        print("Неверный ввод. Установлен режим 1 по умолчанию.")
        TRAINING_MODE = 1

    length = 1 
    if TRAINING_MODE == 2:
        print("кол-во файлов (включая a1.png)")
        try:
            length = int(input())
            if length < 1: length = 1
        except ValueError:
            print("Неверный ввод. Установлено 1 по умолчанию.")
            length = 1
    
    M = 400 
    NOISE_LEVEL_PERCENT = 10 
    
    
    file_a = 'recalled_A_step_00.png'
    A1_vector, width, height = load_image_to_vector(file_a) 
    
    if A1_vector is None:
        print(f"\n Невозможно запустить. Требуется файл '{file_a}'.")
        return
        
    
    save_vector_as_image(A1_vector, width, height, "01_original_A1.png")
    
    training_pairs = []
    
    print("\n--- НАЧАЛО ОБУЧЕНИЯ ---")

    if TRAINING_MODE == 1:
        print("Режим: Две некоррелированные пары (A1 и -A1)")
        
        
        CODE_A1 = create_bipolar_code(M, seed_val=1)
        training_pairs.append((A1_vector, CODE_A1))

        
        A1_neg_vector = [x * -1 for x in A1_vector] 
        CODE_A1_neg = [x * -1 for x in CODE_A1]
        training_pairs.append((A1_neg_vector, CODE_A1_neg))
        
    elif TRAINING_MODE == 2:
        print(f"Режим: Несколько пар (A1 до A{length})")
                
        training_pairs.append((A1_vector, create_bipolar_code(M, seed_val=1)))

        for i in range(2, length + 1): 
            filename = f'a{i}.png'
            A_vector, _, _ = load_image_to_vector(filename)
            
            if A_vector is not None:
                if len(A_vector) != len(A1_vector):
                     print(f"Паттерн '{filename}' имеет другой размер и будет пропущен.")
                     continue
                CODE_Ai = create_bipolar_code(M, seed_val=i)
                training_pairs.append((A_vector, CODE_Ai))
            else:
                print(f"Файл '{filename}' не найден, поиск дополнительных пар прекращен.")
                break
                
    else:
        print("Неверный режим TRAINING_MODE. Установлен 1 по умолчанию.")
        TRAINING_MODE = 1
        return

    if len(training_pairs) < 1:
        print("Недостаточно данных для обучения.")
        return
        
    print(f"Найдено пар для обучения: {len(training_pairs)}")

    bam_model = BidirectionalAssociativeMemory()
    bam_model.train(training_pairs)

    print("\n--- Обучение завершено ---")
    N = len(A1_vector)
    print(f"Размерность паттернов: A ({N}) <-> B ({M})")

    noisy_A1_input = introduce_noise(A1_vector, NOISE_LEVEL_PERCENT)
        
    initial_errors = count_errors(noisy_A1_input, A1_vector)

    save_vector_as_image(noisy_A1_input, width, height, "02_noisy_input_10_percent.png")
    
    print(f"\n--- Восстановление зашумленного '{file_a}' ---")
    
    # --- КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: ПОЛУЧАЕМ ВСЕ ПРОМЕЖУТОЧНЫЕ СОСТОЯНИЯ ---
    recalled_states_A, recalled_B = bam_model.recall(noisy_A1_input)
    # --------------------------------------------------------------------

    target_A = A1_vector
    target_B = training_pairs[0][1] 
    
    # 3. Сохранение всех промежуточных состояний
    print("\n--- Сохранение промежуточных состояний ---")
    
    for i, state_A in enumerate(recalled_states_A):
        filename = f"recalled_A_step_{i:02d}.png"
        save_vector_as_image(state_A, width, height, filename)
        
        # Ошибка относительно идеального (оригинального) вектора
        errors = count_errors(state_A, target_A)
        
        if i == 0:
             print(f"Начальное состояние (Step 00): Ошибок: {errors}")
        elif i == len(recalled_states_A) - 1:
             print(f"Финальное состояние (Step {i:02d}): Ошибок: {errors}")
        else:
             print(f"Промежуточное состояние (Step {i:02d}): Ошибок: {errors}")


    final_recalled_A = recalled_states_A[-1]
    errors_A = count_errors(final_recalled_A, target_A)
    errors_B = count_errors(recalled_B, target_B)
    

    print("\n--- Сводка результатов ---")
    print(f"Входной шумный вектор A: Ошибок: {initial_errors}")
    print(f"Финальный восстановленный вектор A: Ошибок: {errors_A} (Сохранен как recalled_A_step_{len(recalled_states_A) - 1:02d}.png)")
    print(f"Восстановленный код B:   Ошибок: {errors_B}")
    
    if errors_A == 0 and errors_B == 0:
        print("-> Идеальное восстановление! Шум полностью устранен.")
    elif errors_A < initial_errors and errors_B == 0:
        print("-> Успешное восстановление! Сеть устранила большую часть шума.")
    else:
        print("-> Восстановление не идеально. (Вероятно, из-за корреляции в режиме 2 или перегрузки.)")


run_example()