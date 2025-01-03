## Command-line

Command-line usage is available by running ``djicot -h``.

```
usage: djicot [-h] [-c CONFIG_FILE] [-p PREF_PACKAGE]

options:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --CONFIG_FILE CONFIG_FILE
                        Optional configuration file. Default: config.ini
  -p PREF_PACKAGE, --PREF_PACKAGE PREF_PACKAGE
                        Optional connection preferences package zip file (aka data package).
```

## Run as a service / Run forever

1. Add the text contents below a file named `/etc/systemd/system/djicot.service`  
  You can use `nano` or `vi` editors: `sudo nano /etc/systemd/system/djicot.service`
2. Reload systemctl: `sudo systemctl daemon-reload`
3. Enable DJICOT: `sudo systemctl enable djicot`
4. Start DJICOT: `sudo systemctl start djicot`

### `djicot.service` Content
```ini
[Unit]
Description=DJICOT - Display DJI drones in TAK
Documentation=https://djicot.rtfd.io
Wants=network.target
After=network.target

[Service]
RuntimeDirectoryMode=0755
ExecStart=/usr/local/bin/djicot -c /etc/djicot.ini
SyslogIdentifier=djicot
Type=simple
Restart=always
RestartSec=30
RestartPreventExitStatus=64
Nice=-5

[Install]
WantedBy=default.target
```

> Pay special attention to the `ExecStart` line above. You'll need to provide the full local filesystem path to both your djicot executable & djicot configuration files.