from setuptools import setup

setup(
    name='image-editor-practice',
    version='0.1.0',
    py_modules=['main'],
    install_requires=[
        'opencv-python>=4.11.0',
        'Pillow>=10.4.0',
        'numpy>=1.24.4',
    ],
    entry_points={
        'console_scripts': [
            'image-editor=main:main'
        ]
    },
)
