from setuptools import setup

with open('./bbc/BBC-News-Wrapper.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bbc-news',
    version='1.0.1',
    author='Sayad Uddin Tahsin',
    author_email='tahsin.ict@outlook.com',
    description='A simple and yet easy-to-use API for BBC News',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Sayad-Uddin-Tahsin/BBC-News-API',
    packages=['bbc'],
    include_package_data=True,
    package_data={
        '': ['BBC-News-Wrapper.md', 'LICENSE', 'requirements.txt']
    },
    install_requires=[
        'requests>=2.28.2'
    ],
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
    python_requires='>=3.7',
    project_urls={
        'Bug Tracker': 'https://github.com/Sayad-Uddin-Tahsin/bbc-news/issues',
        'PyPI': 'https://pypi.org/project/bbc-news/'
    },
    keywords=['bbc-news', 'bbc-global', 'bbc-api', 'bbc-news-api', 'bbc-api-wrapper', 'tahsin-project']
)
