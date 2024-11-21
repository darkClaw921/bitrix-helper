def calculate_async_recognition_cost(audio_fragments):
    # Цена за единицу тарификации для асинхронного распознавания
    price_per_unit = 0.01  # стоимость за 1 секунду

    total_cost = 0

    for fragment in audio_fragments:
        duration = fragment['duration']
        channels = fragment['channels']

        # Округляем длительность до 1 секунды
        units = (duration + 14) // 15 * 15

        # Округляем количество каналов до четного числа
        channels = (channels + 1) // 2 * 2

        # Рассчитываем стоимость для текущего фрагмента
        fragment_cost = units * channels * price_per_unit
        total_cost += fragment_cost

    return total_cost

# Пример использования функции
audio_fragments = [
    # {'duration': 5, 'channels': 1},
    # {'duration': 37, 'channels': 2},
    # {'duration': 15.5, 'channels': 3},
    {'duration': 600, 'channels': 2}
]

# Расчет стоимости асинхронного распознавания речи
cost = calculate_async_recognition_cost(audio_fragments)
print(f"Стоимость асинхронного распознавания речи: {cost} руб.")