from setuptools import setup

setup(
    name='xblock-gradebook',
    version='0.1',
    description='GradeBook XBlock Tutorial Sample',
    py_modules=['gradebook'],
    install_requires=['XBlock', 'requests'],
    entry_points={
        'xblock.v1': [
            'gradebook = gradebook:GradeBookBlock',
        ]
    }
)