from setuptools import find_namespace_packages, setup


setup(name='xicam.sampleplugin',
      version='1.0.0',
      author='me',
      install_requires='xicam',
      packages=find_namespace_packages(include=['xicam.*']),
      entry_points={
          'xicam.plugins.GUIPlugin': [
              'SamplePlugin=xicam.sampleplugin:SamplePlugin'
          ]
      })
