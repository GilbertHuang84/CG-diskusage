from constant import size_unit, size_diff, size_round


def human_size(number):
    current_idx = 0
    result = float(number)
    while result > size_diff:
        if current_idx >= len(size_unit):
            break
        result = result / size_diff
        current_idx += 1
    return '{} {}'.format(round(result, size_round), size_unit[current_idx])
