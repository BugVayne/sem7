# Индивидуальная лабораторная работа 1 по дисциплине МРЗвИС вариант 1
# Выполнена студентом группы 221702 БГУИР  Кветко Екатерины Дмитриевны
# Файл начала программы, создающий линейную рециркуляционную сеть и сохраняющий результат выполнения программы
# Версия 3. изменено:
#   1. Удалены ручные функции чтения BMP.
#   2. Добавлена библиотека PIL (Pillow) для работы с изображениями.
# Использованные источники:
# Формальные модели обработки информации и параллельные модели решения задач. Практикум: учебно-методическое пособие / В.П.Ивашенко. – Минск: БГУИР, 2020.

import random
import math
from PIL import Image  # Импортируем библиотеку для работы с изображениями

random.seed(0)


# --- Вспомогательные функции для работы с матрицами и векторами ---

def matmul(A, B):
    m = len(A)
    n = len(A[0]) if m > 0 else 0
    p = len(B[0]) if B and len(B) > 0 else 0
    C = [[0.0] * p for _ in range(m)]
    for i in range(m):
        ai = A[i]
        for k in range(n):
            aik = ai[k]
            bk = B[k]
            for j in range(p):
                C[i][j] += aik * bk[j]
    return C


def matvec_mul(A, x):
    m = len(A)
    n = len(A[0]) if m > 0 else 0
    if n != len(x):
        raise ValueError("Размерность вектора не соответствует столбцам матрицы.")
    out = [0.0] * m
    for i in range(m):
        s = 0.0
        row = A[i]
        for j in range(n):
            s += row[j] * x[j]
        out[i] = s
    return out


def transpose(A):
    if not A or not A[0]: return []
    m = len(A)
    n = len(A[0])
    T = [[0.0] * m for _ in range(n)]
    for i in range(m):
        for j in range(n):
            T[j][i] = A[i][j]
    return T


def outer(u, v):
    return [[u_i * v_j for v_j in v] for u_i in u]


def add_inplace(A, B):
    m = len(A)
    n = len(A[0]) if m > 0 else 0
    for i in range(m):
        for j in range(n):
            A[i][j] += B[i][j]


def scalar_mul_matrix(alpha, M):
    return [[alpha * x for x in row] for row in M]


def scalar_mul_vector(alpha, v):
    return [alpha * x for x in v]


def vector_add_inplace(a, b):
    for i in range(len(a)):
        a[i] += b[i]


# --- Функции работы с изображениями через PIL ---

def load_image_to_matrix(path):
    """Читает изображение через PIL и преобразует в матрицу пикселей (список списков кортежей)."""
    try:
        img = Image.open(path).convert('RGB')
        width, height = img.size
        pixels = list(img.getdata())  # Получаем плоский список кортежей (r,g,b)

        # Преобразуем плоский список в двумерную матрицу, как ожидает остальная часть программы
        matrix = []
        for y in range(height):
            # Срез списка для текущей строки
            row = pixels[y * width: (y + 1) * width]
            matrix.append(row)
        return matrix
    except IOError:
        raise ValueError("Не удалось открыть файл изображения.")


def save_matrix_to_image(matrix, path):
    """Сохраняет матрицу пикселей в файл через PIL."""
    if not matrix: return

    height = len(matrix)
    width = len(matrix[0])

    # Создаем новое изображение
    img = Image.new('RGB', (width, height))

    # Преобразуем матрицу обратно в плоский список данных
    flat_data = []
    for row in matrix:
        for pixel in row:
            # pixel должен быть кортежем (r, g, b)
            flat_data.append(tuple(pixel))

    img.putdata(flat_data)
    img.save(path)


# --- Функции Предобработки/Постобработки Изображения ---

def normalize_image(image, Cmax=255):
    h = len(image)
    w = len(image[0]) if h > 0 else 0
    norm = []
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b = image[y][x]
            # Нормализация в диапазон [-1.0, 1.0]
            nr = (2.0 * r / Cmax) - 1.0
            ng = (2.0 * g / Cmax) - 1.0
            nb = (2.0 * b / Cmax) - 1.0
            row.append((nr, ng, nb))
        norm.append(row)
    return norm


def extract_patches_to_vectors(norm_image, ph, pw):
    h = len(norm_image)
    w = len(norm_image[0]) if h > 0 else 0
    patches = []
    # Извлечение неперекрывающихся патчей
    for by in range(0, h, ph):
        if by + ph > h: break
        for bx in range(0, w, pw):
            if bx + pw > w: break
            vec = []
            for cy in range(ph):
                for cx in range(pw):
                    r, g, b = norm_image[by + cy][bx + cx]
                    # R, G, B каналы последовательно в вектор
                    vec.extend([r, g, b])
            patches.append(vec)
    return patches


def vector_to_patch_image(vec, ph, pw, Cmax=255):
    patch = []
    it = iter(vec)
    for y in range(ph):
        row = []
        for x in range(pw):
            r = next(it);
            g = next(it);
            b = next(it)

            # Денормализация из [-1.0, 1.0] обратно в [0, Cmax]
            R_float = (Cmax / 2.0) * (r + 1.0)
            G_float = (Cmax / 2.0) * (g + 1.0)
            B_float = (Cmax / 2.0) * (b + 1.0)

            # Округление и принудительное ограничение
            R = max(0, min(Cmax, int(round(R_float))))
            G = max(0, min(Cmax, int(round(G_float))))
            B = max(0, min(Cmax, int(round(B_float))))

            row.append((R, G, B))
        patch.append(row)
    return patch


def reconstruct_full_image(reconstructed_vectors, H_img, W_img, ph, pw):
    num_patches_w = W_img // pw
    num_patches_h = H_img // ph

    reconstructed_image = [[(0, 0, 0)] * W_img for _ in range(H_img)]

    patch_index = 0
    for by in range(num_patches_h):
        for bx in range(num_patches_w):
            if patch_index >= len(reconstructed_vectors):
                break

            Xr = reconstructed_vectors[patch_index]
            current_patch_img = vector_to_patch_image(Xr, ph, pw)

            for cy in range(ph):
                for cx in range(pw):
                    Y_coord = by * ph + cy
                    X_coord = bx * pw + cx

                    if Y_coord < H_img and X_coord < W_img:
                        reconstructed_image[Y_coord][X_coord] = current_patch_img[cy][cx]

            patch_index += 1

    return reconstructed_image


# --- Функции Модели Рециркуляции ---

def init_weights(input_dim, hidden_dim, scale=0.01):
    # Wf: Кодирующая матрица [hidden_dim x input_dim]
    Wf = [[(random.random() * 2 - 1) * scale for _ in range(input_dim)] for __ in range(hidden_dim)]
    # Wb: Декодирующая матрица [input_dim x hidden_dim]
    Wb = [[(random.random() * 2 - 1) * scale for _ in range(hidden_dim)] for __ in range(input_dim)]
    return Wf, Wb


def reconstruct_vector(X, Wf, Wb):
    """ Кодирует X в Y и затем декодирует Y в Xr. """

    # Прямой проход (Кодирование): Y = Wf * X
    Y = matvec_mul(Wf, X)
    # Обратный проход (Декодирование): Xr = Wb * Y
    XXr = matvec_mul(Wb, Y)

    # Ограничение выходных значений в диапазон [-1.0, 1.0]
    Xr = [0.0] * len(XXr)
    for i in range(len(XXr)):
        clamped_value = max(-1.0, min(1.0, XXr[i]))
        Xr[i] = clamped_value

    return Xr, Y


# --- ФУНКЦИЯ ОБУЧЕНИЯ ---

def train_linear_recirculation(Xs, hidden_dim, eta=0.001, epochs=1, loss_threshold=None, verbose=False):
    """
    Обучает модель Линейной Рециркуляции с использованием Стохастического Градиентного Спуска (SGD).
    """
    if not Xs:
        raise ValueError("Нет входных векторов Xs.")
    input_dim = len(Xs[0])

    Wf, Wb = init_weights(input_dim, hidden_dim, scale=0.01)

    print(f"\n--- Начало обучения ({'SGD'}) ---")

    # Стохастический Градиентный Спуск: обновление весов после каждого патча (X)
    for epoch in range(epochs):
        total_loss = 0.0

        for X in Xs:
            # 1. Прямой проход (Y = Wf * X)
            Y = matvec_mul(Wf, X)

            # 2. Обратный проход (Xr = Wb * Y)
            Xr = matvec_mul(Wb, Y)

            # 3. Ошибка реконструкции e = X - Xr
            e = [X[i] - Xr[i] for i in range(input_dim)]

            # Накопление ошибки (Loss) L = 0.5 * ||e||^2
            total_loss += sum(ei * ei for ei in e) * 0.5

            # 4. Вычисление Градиента для Wb (Декодер)
            # dWb = e * Y^T
            dWb = outer(e, Y)

            # 5. Вычисление Градиента для Wf (Кодер)
            # Отраженная ошибка e_hat = Wb^T * e
            WbT = transpose(Wb)
            WbT_e = matvec_mul(WbT, e)
            # dWf = e_hat * X^T
            dWf = outer(WbT_e, X)

            # 6. Обновление весов (SGD)
            # Wb = Wb + eta * dWb
            add_inplace(Wb, scalar_mul_matrix(eta, dWb))
            # Wf = Wf + eta * dWf
            add_inplace(Wf, scalar_mul_matrix(eta, dWf))

        # Расчет средней потери за эпоху
        avg_loss = total_loss / len(Xs)

        if verbose:
            print(f"Epoch {epoch + 1}/{epochs} | Avg Loss: {avg_loss:.6f}")

        # Условие выхода по порогу ошибки
        if loss_threshold is not None and avg_loss < loss_threshold:
            print(f"Достигнут порог ошибки ({loss_threshold:.6f}) на эпохе {epoch + 1}. Обучение остановлено.")
            break

    print("--- Обучение завершено ---\n")
    return Wf, Wb


# --- Главный Блок ---

if __name__ == "__main__":
    img_path = "Peppers.bmp"
    try:
        # Используем новую функцию на основе PIL
        img = load_image_to_matrix(img_path)
        print("Изображение прочитано. Размер:", len(img[0]), "x", len(img))
    except Exception as e:
        print("Библиотека PIL не смогла прочитать файл. Убедитесь, что 'input.bmp' существует.", e)
        img = None

    if img:
        norm = normalize_image(img, Cmax=255)
        H_img = len(norm)
        W_img = len(norm[0])

        ph, pw = 8, 8  # Размер патча 8x8
        patches = extract_patches_to_vectors(norm, ph, pw)
        print("Патчей:", len(patches), "векторный размер одного патча:", len(patches[0]) if patches else 0)

        input_dim = len(patches[0])  # 8*8*3 = 192
        hidden_dim = 64

        # Обучение
        Wf, Wb = train_linear_recirculation(
            Xs=patches,
            hidden_dim=hidden_dim,
            eta=0.001,
            epochs=100,
            loss_threshold=0.005,
            verbose=True
        )

        # --- Сводка по Сжатию (с учетом битов на пиксель) ---
        H = hidden_dim
        N_patches = len(patches)

        # Имитация разреженности: доля активаций Y, которые нужно сохранить (для сжатия)
        p = 0.01

        BITS_PER_CHANNEL = 8
        CHANNELS_PER_PIXEL = 3
        BITS_PER_PIXEL = BITS_PER_CHANNEL * CHANNELS_PER_PIXEL  # 24
        BITS_PER_FLOAT = 32  # Стандартно для float32

        # P_num_bits: Размер исходного изображения в битах (24 bpp)
        P_num_bits = W_img * H_img * BITS_PER_PIXEL

        # W_bits: Объем весов Wf и Wb в битах
        W_bits = (H * input_dim + input_dim * H) * BITS_PER_FLOAT

        # Y_sparse_bits: Объем сохраненных разреженных активаций Y (N_patches * H * p)
        # Это модель сжатия, где сохраняется только p% активаций Y для каждого патча.
        Y_sparse_bits = (N_patches * H * p) * BITS_PER_FLOAT

        # Z_denom_bits: Общий объем данных, которые нужно сохранить для реконструкции
        Z_denom_bits = W_bits + Y_sparse_bits

        Q_compression = P_num_bits / Z_denom_bits if Z_denom_bits else 0.0

        print("\n--- Сводка по Сжатию (для оценки) ---")
        print(f"Размер исходного изображения: {W_img} x {H_img}")
        print(f"Размер скрытого слоя (H): {H}")
        print(f"Пользовательский параметр разреженности (p): {p}")
        print("---")
        print(f"Общий объем ИСХОДНОГО Изображения: {P_num_bits} бит")
        print(f"Объем весов Wf, Wb: {round(W_bits, 2)} бит")
        print(f"Объем разреженных активаций Y (при p={p}): {round(Y_sparse_bits, 2)} бит")
        print(f"Общий объем СОХРАНЕННЫХ данных (Z_denom): {round(Z_denom_bits, 2)} бит")
        print(f"Коэффициент сжатия Q = P_num / Z_denom: {round(Q_compression, 2)}")
        print("--------------------------------------\n")

        print("Начинаем полную реконструкцию изображения...")
        reconstructed_vectors = []
        for X in patches:
            # Используем обученные Wf и Wb для кодирования/декодирования
            Xr, _ = reconstruct_vector(X, Wf, Wb)
            reconstructed_vectors.append(Xr)

        full_reconstructed_img = reconstruct_full_image(reconstructed_vectors, H_img, W_img, ph, pw)

        print(f"Полное изображение восстановлено. Размер: {W_img} x {H_img}")

        output_path = "reconstructed_output_2.bmp"
        try:
            # Используем новую функцию на основе PIL
            save_matrix_to_image(full_reconstructed_img, output_path)
            print(f"Восстановленное изображение сохранено как: {output_path}")
        except Exception as save_e:
            print(f"Ошибка при сохранении изображения: {save_e}")

    else:
        print("Работа программы остановлена, так как не удалось прочитать 'input.bmp'.")