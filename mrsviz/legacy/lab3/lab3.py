# Индивидуальная лабораторная работа 3 по дисциплине МРЗвИС вариант 1
# Выполнена студентом группы 221702 БГУИР  Кветко Екатерины Дмитриевны
# Файл реализовывает модель сети Джордана с логарифмической функцией активации (гиперболический арксинус)
# Использованные источники:
# Формальные модели обработки информации и параллельные модели решения задач. Практикум: учебно-методическое пособие / В.П.Ивашенко. – Минск: БГУИР, 2020.

import numpy as np
import random
import math

np.random.seed(42)
random.seed(42)


class DataScaler:
    def __init__(self, data_list):
        self.data_min = np.min(data_list)
        self.data_max = np.max(data_list)
        self.range = self.data_max - self.data_min
        if self.range == 0:
            self.range = 1.0 
        self.epsilon = 1e-8

    def normalize(self, value):
        return (value - self.data_min) / (self.range + self.epsilon)

    def denormalize_raw(self, value):
        return value * self.range + self.data_min


class JordanRNN:
    def __init__(self, input_size, hidden_size, output_size, learning_rate):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.context_size = output_size
        self.learning_rate = learning_rate
        
        self.W_ih = self._initialize_weights(self.input_size + self.context_size, self.hidden_size)
        self.W_ho = self._initialize_weights(self.hidden_size, self.output_size)
        self.b_h = np.zeros((1, self.hidden_size))
        self.b_o = np.zeros((1, self.output_size))
        self.context_layer = np.zeros((1, self.context_size)) 


    def _initialize_weights(self, rows, cols):
        limit = np.sqrt(6 / (rows + cols))
        return np.random.uniform(-limit, limit, size=(rows, cols))

    
    def _activation_hidden(self, x):
        return np.arcsinh(x)

    def _activation_hidden_derivative(self, x):
        return 1.0 / np.sqrt(x**2 + 1.0)


    def _activation_effector(self, x):
        return x 

    def _activation_effector_derivative(self, x):
        return np.ones_like(x) # f'(x) = 1


    def forward(self, input_vector):
        X = input_vector.reshape(1, self.input_size)
        X_combined = np.hstack((X, self.context_layer))
        
        H_input = np.dot(X_combined, self.W_ih) + self.b_h
        H_output = self._activation_hidden(H_input)
        
        O_input = np.dot(H_output, self.W_ho) + self.b_o
        output = self._activation_effector(O_input)
        
        self.context_layer = output.copy()
        return output, X_combined, H_input, H_output, O_input

    def backward(self, target, output, X_combined, H_input, H_output, O_input):
        d_output = output - target
        d_output_layer = d_output * self._activation_effector_derivative(O_input) 

        d_W_ho = np.dot(H_output.T, d_output_layer)
        d_b_o = np.sum(d_output_layer, axis=0, keepdims=True)
        
        d_H_output = np.dot(d_output_layer, self.W_ho.T)
        d_H_input = d_H_output * self._activation_hidden_derivative(H_input)

        d_W_ih = np.dot(X_combined.T, d_H_input)
        d_b_h = np.sum(d_H_input, axis=0, keepdims=True)
        
        self.W_ho -= self.learning_rate * d_W_ho
        self.b_o -= self.learning_rate * d_b_o
        self.W_ih -= self.learning_rate * d_W_ih
        self.b_h -= self.learning_rate * d_b_h

    def reset_context(self):
        self.context_layer = np.zeros((1, self.context_size))

    def train(self, training_data_normalized, max_iterations, max_error):
        self.reset_context() 
        
        for iteration in range(max_iterations):
            total_error = 0
            random.shuffle(training_data_normalized)
            
            for input_list, target_list in training_data_normalized:
                input_arr = np.array(input_list)
                target_arr = np.array(target_list).reshape(1, self.output_size)
                
                output, X_combined, H_input, H_output, O_input = self.forward(input_arr)
                self.backward(target_arr, output, X_combined, H_input, H_output, O_input)
                
                total_error += np.sum(np.power(target_arr - output, 2))

            avg_error = total_error / len(training_data_normalized)
            
            if avg_error < max_error:
                print(f"Обучение завершено. Итераций: {iteration + 1}, Ошибка: {avg_error:.8f}")
                break

            if (iteration + 1) % 50000 == 0:
                print(f"Итерация: {iteration + 1}, Ошибка: {avg_error:.8f}")
                
        if iteration == max_iterations - 1:
             print(f"Обучение завершено по лимиту. Итераций: {iteration + 1}, Ошибка: {avg_error:.8f}")

    def predict(self, input_vector):
        output, _, _, _, _ = self.forward(input_vector)
        return output.flatten()





WIN_SIZE = 2      
HIDDEN_SIZE = 15  
EFFECTORS = 3     
LEARNING_RATE = 0.001 
MAX_ERROR = 0.00001 
MAX_ITERATIONS = 500000 

full_sequence = np.arange(1, 14) 
scaler = DataScaler(full_sequence)

training_data = [
([0, 1], [1, 2, 3]),
([1, 1], [2, 3, 5]),
([1, 2], [3, 5, 8]),
([2, 3], [5, 8, 13]),
([3, 5], [8, 13, 21]),
([5, 8], [13, 21, 34])
]
'''
training_data = [
([1, 2], [1, 2, 3]),
([2, 3], [3, 4, 5]),
([3, 4], [5, 6, 7]),
([4, 5], [6, 7, 8]),
([5, 6], [7, 8, 9]),
([6, 7], [8, 9, 10])
]'''



training_data_normalized = []
for inputs, targets in training_data:
    norm_inputs = [scaler.normalize(i) for i in inputs]
    norm_targets = [scaler.normalize(t) for t in targets]
    training_data_normalized.append((norm_inputs, norm_targets))

model = JordanRNN(
    input_size=WIN_SIZE, 
    hidden_size=HIDDEN_SIZE, 
    output_size=EFFECTORS,
    learning_rate=LEARNING_RATE
)

print(f"--- Запуск обучения сети Джордана ---")

model.train(training_data_normalized, max_iterations=MAX_ITERATIONS, max_error=MAX_ERROR)


model.reset_context() 
for input_list, _ in training_data_normalized:
    model.predict(np.array(input_list))

input_for_predict_raw = np.array([8.0, 13.0])
input_for_predict_norm = np.array([scaler.normalize(v) for v in input_for_predict_raw])

prediction_block_norm = model.predict(input_for_predict_norm)

expected = [21, 34, 55]
print("\n--- Результаты прогнозирования---")
print(f"Входное окно для прогноза: {input_for_predict_raw.tolist()}")
print(f"Ожидаемый блок (Exp): {expected}")

for i, (exp, act_norm) in enumerate(zip(expected, prediction_block_norm)):
    act_raw = scaler.denormalize_raw(act_norm)
    print(f"{i+1}. Ожидание: {exp} получено: {act_raw:.5f}")