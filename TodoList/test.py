def check_unique_length(word):
    current_length = 0
    unique_characters = []
    max_length = 0
    for letter in word:
        if letter not in unique_characters:
            current_length += 1
            unique_characters.append(letter)

        elif letter in unique_characters:
            if current_length > max_length:
                max_length = current_length
            unique_characters = [letter]
            current_length = 1

    if current_length > max_length:
        max_length = current_length

    return max_length


print(check_unique_length("abcdabcde"))
