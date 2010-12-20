from setuptools import setup, find_packages
import os

version = '1.1dev'

def product_path(filename):
    return os.path.join("Products", "SilvaForum", filename)

setup(name='Products.SilvaForum',
      version=version,
      description="Forum for Silva",
      long_description=open(product_path("README.txt")).read() + "\n" + \
          open(product_path("HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='forum silva zope2',
      author='Infrae',
      author_email='info@infrae.com',
      url='http://infrae.com/products/silva',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'five.grok',
        'setuptools',
        'silva.batch',
        'silva.captcha',
        'silva.core.views',
        'silva.core.interfaces',
        'silva.translations',
        'Products.Silva',
        'Products.SilvaMetadata',
        'zeam.utils.batch',
        'zope.component',
        'zope.interface',
        ],
      )
