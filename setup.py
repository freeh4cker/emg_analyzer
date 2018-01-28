from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


version = '0.1bRC1'
setup(
    name='emg_analyzer',
    version=version,
    maintainer='Bertrand Neron',
    maintainer_email='freeh4cker@gmail.com',
    author='Bertrand Neron',
    author_email='freeh4cker@gmail.com',
    long_description=long_description,
    keywords=['EMG', 'data science', 'data normalization'],
    description='parse emg recording and normalize the voltage',
    license='BSD3',
    platforms=['Unix', 'Linux', 'MacOsX'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Environment :: Console',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    zip_safe=False,
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=open("requirements.txt").read().split(),

    entry_points={
        'console_scripts': [
           'emg_norm=emg_analyzer.scripts.emg_norm:main',
           'emg_group_tracks=emg_analyzer.scripts.emg_group_tracks:main',
        ]
    }

)
