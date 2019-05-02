import os
import re

from setuptools import find_packages, setup

PACKAGE_NAME = 'intracing'

OPENTRACING_INSTRUMENTATION_LINK = (
    'git+https://github.com/Jamim/opentracing-python-instrumentation.git'
    '@fix/boto3-dynamodb-describe-table'
    '#egg=opentracing_instrumentation'
)


def get_version():
    init_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), PACKAGE_NAME, '__init__.py'
    )
    with open(init_path) as init_file:
        return re.search(
            r"^__version__ = '(?P<version>.*?)'.*$",
            init_file.read(), re.MULTILINE
        ).group('version')


setup(
    python_requires='>=2.7',
    author='Aliaksei Urbanski',
    author_email='aliaksei@inspectorio.com',
    url='https://gitlab.inspectorio.com/saas/libs/inspectorio-tracing',
    name=PACKAGE_NAME,
    version=get_version(),
    description='Inspectorio Tracing Helper',
    install_requires=[
        'jaeger-client<4',
        'opentracing<2',
        'opentracing-instrumentation @ ' + OPENTRACING_INSTRUMENTATION_LINK,
        'six',
    ],
    extras_require={
        'django': ['django_opentracing==0.1.20'],
        'flask': ['flask-opentracing==0.2.0'],
    },
    packages=find_packages(
        exclude=['tests']
    )
)
