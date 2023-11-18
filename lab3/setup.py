from setuptools import setup, Extension

module = Extension(
    'OpenMP_funcs',
    sources=['OpenMP_funcs.c'],
    extra_compile_args=['-fopenmp', '-lopenmp'],
    extra_link_args=['-fopenmp', '-lopenmp'],
)

setup(
    name='OpenMP_funcs',
    version='1.0',
    ext_modules=[module],
)
