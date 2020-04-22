# ckanext-dataportal

CKAN extensions to customize the [ILRI Data Portal](https://data.ilri.org/portal/).

## Installation
With your CKAN virtual environment activated, install each extention as follows:

```console
$ python setup.py develop
$ pip install -r requirements.txt
```

## Extra Setup For ckanext-ilrimetadata
The `ckanext-ilrimetadata` extension requires the MySQLToFile program from the [meta](https://github.com/ilri/meta) toolset. See the installation instructions there and configure relevant settings in `config/production.ini`.
