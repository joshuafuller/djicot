To report bugs, enable debug logging by setting the `DEBUG=1` environment variable:

```sh
DEBUG=1 djicot
```

Alternatively, you can use:

```sh
export DEBUG=1
djicot
```

Or update the configuration file:

```sh
echo 'DEBUG=1' >> djicot.ini
djicot -c djicot.ini
```

To view logs using systemd, run:

```sh
journalctl -fu djicot
```

For support, please use GitHub issues. Note that DJICOT is free open source software and comes with no warranty. See LICENSE for details.
