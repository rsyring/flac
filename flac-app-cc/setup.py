from setuptools import setup


setup(
    name='jax',
    entry_points={
        'console_scripts': [
            'jax=jax.app:cli'
        ],
    },
)
