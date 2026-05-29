name = "usd_tools_example"
version = "0.1.0"

requires = ["usd-26.05"]


def commands():
    env.PYTHONPATH.prepend("{root}/python")
