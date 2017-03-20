import functools


class LargeNumber:
    def __init__(self, num=0):
        self.raw_num = num
        self._number = []
        self.coefficient = (1 if num >= 0 else -1)
        self.remainder = 0
        for chara in str(self.raw_num):
            try:
                self._number.insert(0, int(chara))
            except ValueError:
                continue

    def get_value(self):
        return self._number[::-1]

    def set_value(self, number):
        self._number = number[::-1]

    def print_value(self):
        temp_value = self._number[::-1]
        result = '' if self.coefficient == 1 else '-'
        if len(temp_value) == 1:
            result += str(temp_value[0])
        else:
            result += functools.reduce(lambda x, y: str(x) + str(y), temp_value)
        return result

    def inverted_value(self):
        return self._number

    def toggle_coe(self):
        self.coefficient *= -1

    def shift_left(self, amount=1):
        for _ in range(amount):
            self._number.insert(0, 0)

    def shift_right(self, amount=1):
        for _ in range(amount):
            self._number = self._number[1:]

    def multiply(self, number2):
        str_number = number2.inverted_value()
        result_number = LargeNumber()
        for index, num in enumerate(str_number):
            tem_number = multiply_one_digit(self.get_value(), num)
            tem_number.shift_left(index)
            result_number.add(tem_number)
        self.coefficient *= number2.coefficient
        self._number = result_number.inverted_value()

    def subtract(self, large_number):
        if large_number.coefficient == -1 and self.coefficient == 1:
            large_number.toggle_coe()
            self.real_add(large_number)
            return
        if self.coefficient == -1 and large_number.coefficient == 1:
            self.toggle_coe()
            self.real_add(large_number)
            self.toggle_coe()
            return
        source_is_larger = self.larger_than(large_number)
        if self.coefficient == large_number.coefficient:
            if source_is_larger:
                self.real_subtract(large_number)
            else:
                large_number.real_subtract(self)
                self._number = large_number.inverted_value()
                self.coefficient *= -1

    def add(self, large_number):
        if large_number.coefficient == -1 and self.coefficient == 1:
            large_number.coefficient = 1
            self.subtract(large_number)
            return
        if self.coefficient == -1 and large_number.coefficient == 1:
            self.toggle_coe()
            self.subtract(large_number)
            self.toggle_coe()
            return
        if self.coefficient == large_number.coefficient:
            self.real_add(large_number)

    def real_subtract(self, large_number):
        str_number = large_number.inverted_value()
        source_number = self._number
        carrier = False
        for index, num in enumerate(str_number):
            if index >= len(source_number):
                temp_value = int(str_number[index]) + (-1 if carrier else 0)
            else:
                temp_value = -int(str_number[index]) + (-1 if carrier else 0) + source_number[index]
            if temp_value < 0:
                current_value = (temp_value + 10) % 10
            else:
                current_value = temp_value % 10
            if index < len(source_number):
                source_number[index] = current_value
            else:
                source_number.append(current_value)
            carrier = temp_value < 0
        if carrier:
            source_number[len(str_number)] -= 1
        self.set_value(source_number[::-1])

    def real_add(self, large_number):
        str_number = large_number.inverted_value()
        source_number = self._number
        carrier = False
        for index, num in enumerate(str_number):
            if index >= len(source_number):
                temp_value = int(str_number[index]) + (1 if carrier else 0)
            else:
                temp_value = int(str_number[index]) + (1 if carrier else 0) + source_number[index]
            current_value = temp_value % 10
            if index < len(source_number):
                source_number[index] = current_value
            else:
                source_number.append(current_value)
            carrier = temp_value >= 10
        if carrier:
            source_number.append(1)
        self._number = source_number

    def delete_high_zero(self):
        while len(self._number) > 1 and self._number[-1] == 0:
            self._number = self._number[:-1]

    def larger_than(self, large_number):
        source_is_larger = True
        if len(self.get_value()) > len(large_number.get_value()):
            source_is_larger = True
        elif len(self.get_value()) == len(large_number.get_value()):
            inverted_dst = large_number.get_value()
            for index, num in enumerate(self.get_value()):
                if num > inverted_dst[index]:
                    source_is_larger = True
                    break
                elif num < inverted_dst[index]:
                    source_is_larger = False
                    break
        else:
            source_is_larger = False
        return source_is_larger

    def divide(self, large_number):
        number_one = LargeNumber(1)
        src_coe = self.coefficient
        dst_coe = self.coefficient
        self.coefficient = 1
        large_number.coefficient = 1

        tem_self = LargeNumber()
        tem_self.set_value(self.get_value())
        result_number = LargeNumber(0)

        tem_result = real_divide(tem_self, large_number)
        result_number.add(tem_result)
        while tem_result.remainder.larger_than(large_number):
            tem_result = real_divide(tem_self, large_number)
            result_number.add(tem_result)
            result_number.remainder = tem_result.remainder
        self.remainder = result_number.remainder.get_value()
        self.set_value(result_number.get_value())
        self.coefficient = src_coe * dst_coe


def multiply_one_digit(large_number, digit):
    result_number = LargeNumber()
    source_number = large_number
    carrier = 0
    for index, num in enumerate(large_number[::-1]):
        tem_value = num * digit + carrier
        carrier = tem_value // 10
        source_number[index] = tem_value % 10
    if carrier > 0:
        source_number.append(carrier)
    result_number.set_value(source_number[::-1])
    return result_number


def real_divide(number1, number2):
    large_number = LargeNumber()
    large_number.set_value(number2.get_value())
    constant_a = len(number1.get_value()) - len(large_number.get_value())
    result = LargeNumber(0)
    number_one = LargeNumber(1)
    if constant_a < 0:
        result.remainder = number2
        return result

    large_number.shift_left(constant_a)
    if not number1.larger_than(large_number):
        large_number.shift_right()
        constant_a -= 1
    while number1.larger_than(large_number):
        number1.subtract(large_number)
        number1.delete_high_zero()
        result.add(number_one)
    number1.delete_high_zero()
    constant_coe = LargeNumber(10 ** constant_a)
    result.multiply(constant_coe)
    result.remainder = number1
    return result


num1 = LargeNumber(6234)
num2 = LargeNumber(3)
num1.divide(num2)
print(num1.print_value())
