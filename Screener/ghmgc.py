
import atexit

names = ['Geeks', 'for', 'Geeks']

def hello(name):
    print (name)

for name in names:

    # Using register()
    atexit.register(hello, name)
