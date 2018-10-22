import constant


def human_size(number):
    current_idx = 0
    result = float(number)
    while result > constant.size_diff:
        if current_idx >= len(constant.size_unit):
            break
        result = result / constant.size_diff
        current_idx += 1
    return '{} {}'.format(round(result, constant.size_round), constant.size_unit[current_idx])
