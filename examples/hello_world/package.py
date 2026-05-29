name = "hello_world"
version = "1.0.0"

requires = []


def commands():
    env.PATH.prepend("{root}/bin")
