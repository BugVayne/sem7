# Индивидуальная лабораторная работа (аналог)
# Тема: Модель сети Хопфилда (Дискретное время, Асинхронный режим, Метод проекций)

from PIL import Image
import random
import numpy as np  # Numpy необходим для метода проекций (псевдообратная матрица)
import copy
import os


def load_image_to_vector(file_path):
    """Загружает изображение и преобразует его в биполярный вектор (-1, 1)."""
    try:
        img = Image.open(file_path).convert('L')
        # Бинаризация: <128 -> черный (1), >=128 -> белый (-1)
        # Обратите внимание: обычно в Хопфилде 1 - это активный нейрон (черный пиксель)
        data = np.array(img.getdata())
        vector = np.where(data < 128, 1, -1)

        width, height = img.size
        print(f"Загружено '{file_path}'. Размер: {width}x{height} ({len(vector)} нейронов)")

        return vector, width, height

    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
        return None, None, None
    except Exception as e:
        print(f"Ошибка при обработке изображения '{file_path}': {e}")
        return None, None, None


def save_vector_as_image(vector, width, height, filename):
    """Сохраняет вектор обратно в изображение."""
    try:
        # Преобразуем 1 -> 0 (черный), -1 -> 255 (белый)
        pixel_data = [0 if val == 1 else 255 for val in vector]

        img = Image.new('L', (width, height))
        img.putdata(pixel_data)
        img.save(filename)
        print(f"Изображение сохранено: {filename}")

    except Exception as e:
        print(f"Ошибка при сохранении изображения '{filename}': {e}")


def introduce_noise(vector, noise_percentage):
    """Вносит шум инверсией битов."""
    noisy_vector = vector.copy()
    N = len(noisy_vector)

    num_corrupt = int(N * noise_percentage / 100)
    indices = np.random.choice(N, num_corrupt, replace=False)

    noisy_vector[indices] *= -1

    print(f"Введен шум: инвертировано {num_corrupt} пикселей ({noise_percentage}%)")
    return noisy_vector


def count_errors(v1, v2):
    """Считает количество несовпадающих элементов."""
    if len(v1) != len(v2): return -1
    return np.sum(v1 != v2)


class DiscreteHopfieldNetwork:
    def __init__(self):
        self.weights = None
        self.num_neurons = 0

    def train_projection(self, patterns):
        """
        Обучение методом проекций (через псевдообратную матрицу).
        W = X^T * (X * X^T)^-1 * X  (в упрощенном виде через pinv)
        """
        if not patterns: return

        # X - матрица образов (M x N), где M - кол-во образов, N - нейроны
        X = np.array(patterns)
        self.num_neurons = X.shape[1]

        print("Начало обучения методом проекций...")
        # W = X.T * pinv(X.T)
        X_T = X.T
        self.weights = np.dot(X_T, np.linalg.pinv(X_T))

        # Обнуляем диагональ (нейрон не связан сам с собой - условие стабильности)
        np.fill_diagonal(self.weights, 0)
        print("Матрица весов рассчитана.")

    def _activation(self, value, current_state):
        """
        Модифицированная функция знака.
        Если сумма = 0, состояние не меняется.
        """
        if value > 0:
            return 1
        elif value < 0:
            return -1
        else:
            return current_state

    def recall_asynchronous(self, input_vector, max_epochs=100):
        """
        Асинхронное восстановление.
        Возвращает список состояний (историю изменений) для визуализации.
        """
        current_state = np.array(input_vector, dtype=float)
        history = [current_state.copy()]  # Сохраняем начальное состояние

        N = self.num_neurons
        indices = np.arange(N)

        print("Запуск релаксации (асинхронный режим)...")

        for epoch in range(max_epochs):
            state_changed = False

            # Перемешиваем порядок обновления нейронов (Асинхронность)
            np.random.shuffle(indices)

            for i in indices:
                # Взвешенная сумма для i-го нейрона
                net = np.dot(self.weights[i], current_state)

                # Применение функции активации
                new_val = self._activation(net, current_state[i])

                if new_val != current_state[i]:
                    current_state[i] = new_val
                    state_changed = True

            # Сохраняем состояние после эпохи
            history.append(current_state.copy())

            # Условие выхода: если за полную эпоху не было изменений
            if not state_changed:
                print(f"Сходимость достигнута за {epoch + 1} эпох.")
                break
        else:
            print(f"Достигнут лимит эпох ({max_epochs}).")

        return history


def run_hopfield_example():
    print("Выберите режим обучения:")
    print("1 - Один образ (запомнить и восстановить)")
    print("2 - Несколько образов (a1.png, a2.png ...)")

    try:
        MODE = int(input("Ваш выбор: "))
    except ValueError:
        MODE = 1

    training_patterns = []

    # Файл для теста (он должен существовать)
    target_file = 'a1.png'  # Предполагаем, что файлы называются a1.png, a2.png...

    # 1. Загрузка данных
    if MODE == 1:
        vec, w, h = load_image_to_vector(target_file)
        if vec is None: return
        training_patterns.append(vec)

    elif MODE == 2:
        print("Сколько файлов загрузить?")
        try:
            count = int(input())
        except:
            count = 2

        for i in range(1, count + 1):
            fname = f'a{i}.png'
            vec, w, h = load_image_to_vector(fname)
            if vec is not None:
                training_patterns.append(vec)
            else:
                break
        if not training_patterns: return

    # Проверка размеров (все должны быть одинаковыми)
    ref_len = len(training_patterns[0])
    if any(len(p) != ref_len for p in training_patterns):
        print("Ошибка: изображения имеют разный размер!")
        return

    width, height = w, h  # Используем размеры последнего загруженного

    # 2. Обучение сети
    net = DiscreteHopfieldNetwork()
    net.train_projection(training_patterns)

    # 3. Подготовка теста (берем первый образ и шумим его)
    test_pattern = training_patterns[0]

    # Сохраняем эталон
    save_vector_as_image(test_pattern, width, height, "00_original.png")

    # Добавляем шум
    NOISE_LEVEL = 15  # Процентов
    noisy_input = introduce_noise(test_pattern, NOISE_LEVEL)
    initial_errors = count_errors(noisy_input, test_pattern)

    save_vector_as_image(noisy_input, width, height, "01_noisy_input.png")

    # 4. Восстановление
    history_states = net.recall_asynchronous(noisy_input)

    # 5. Сохранение результатов и статистика
    print("\n--- Результаты восстановления ---")

    for i, state in enumerate(history_states):
        # Сохраняем каждый шаг (или каждый 2-й, если их много, чтобы не забивать диск)
        filename = f"step_{i:02d}.png"
        save_vector_as_image(state, width, height, filename)

        errs = count_errors(state, test_pattern)
        print(f"Шаг {i}: Ошибок относительно эталона: {errs}")

    final_state = history_states[-1]
    final_errors = count_errors(final_state, test_pattern)

    print("\n--- Итог ---")
    print(f"Ошибок в начале: {initial_errors}")
    print(f"Ошибок в конце:  {final_errors}")

    if final_errors == 0:
        print("-> Идеальное восстановление!")
    else:
        print("-> Остаточный шум или ложный аттрактор.")


if __name__ == "__main__":
    # Создадим фиктивное изображение a1.png для теста, если его нет
    if not os.path.exists("a1.png"):
        print("Создаю тестовое изображение a1.png (буква T)...")
        img = Image.new('L', (10, 10), 255)  # Белый фон
        pixels = img.load()
        for x in range(10): pixels[x, 0] = 0  # Верхняя черта
        for y in range(10): pixels[5, y] = 0  # Вертикальная черта
        img.save("a1.png")

    run_hopfield_example()