Truescobi = "(()(()))"
Falsescobe = "())()()"
TEST = '[{}]'
testt = '[{()]}'

dictt = {
    ")": "(",
    "]": "[",
    "}": "{",
}

open_scobes = ["(", "[", "{"]



def all_variants(number):
    ...
    

def a_golqm(text):
    opens = []
    for i in text:
        if i in open_scobes:
            opens.append(i)
        else:
            last_elem = opens[-1]
            if last_elem == dictt[i]:
                opens.pop()
            else:
                return False
    return True if len(opens) == 0 else False


def b(text):
    counter = 0
    for i in text:
        if i == "(":
            counter += 1
        elif i == ")":
            counter -= 1
        else:
            return False
        if counter < 0:
            return False
    return True if counter == 0 else False


if __name__ == "__main__":
    print(b(Truescobi))
    print(b(Falsescobe))