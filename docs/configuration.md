DJICOT's configuration parameters can be set two ways:

1. In an INI-style configuration file. (ex. ``djicot -c config.ini``)
2. As environment variables. (ex. ``export DEBUG=1;djicot``)

DJICOT has the following built-in configuration parameters:

* **`FEED_URL`**:
    * Default: ``tcp://192.168.1.10:41030``

    DJI data source URL. 

Additional configuration parameters, including TAK Server configuration, are included in the [PyTAK Configuration](https://pytak.readthedocs.io/en/latest/configuration/) documentation.





