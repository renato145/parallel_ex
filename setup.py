import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="parallel_ex",
    version="0.1",
    # author="Renato Hermoza",
    # author_email="renato.hermozaaragones@adelaide.edu.au",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/renato145/parallel_ex",
    # packages=setuptools.find_packages(),
    packages=['parallel_ex'],
)
