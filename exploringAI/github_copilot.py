

# Write a program which will find all such numbers which are divisible by n but are not a multiple of m,
# between 2000 and 3200, The numbers obtained should be printed in a comma-separated sequence on a single line.
# add check if both n and m are not 0 or negative or bigger than 2000

def find_numbers(n, m):
    listt = []
    for i in range(2000, 3201):
        if i % n == 0 and i % m != 0:
            listt.append(i)
    return listt



print(find_numbers(15, 5))


# def sum_even_number(listt):
#     sum = 0
#     for i in listt:
#         if i % 2 == 0:
#             sum += i
#     return sum
#
#
# # generate list of numbers between 2000 and 3200
# listt = list(range(2000, 3201))
# print(sum_even_number(listt)    )


