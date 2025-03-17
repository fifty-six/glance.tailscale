# Tailscale Extension for Glance

A simple extension for Glance which allows viewing the devices in your tailnet, their statues, and their ips.


## Preview
[<img src="https://github.com/user-attachments/assets/67983ed2-7c7b-4165-a985-f96d4d22e312" alt="Screenshot showing devices with machine names, statuses, and (on-hover) an ip address" width="250">](https://github.com/user-attachments/assets/67983ed2-7c7b-4165-a985-f96d4d22e312)

<video src="https://github.com/user-attachments/assets/d5d7edb8-c142-4d40-a879-a766b5703ec4" alt="Video showing on-hover behavior"> </video>

IP addresses are shown on hover, connection statuses can be toggled with `show_status`, and update statuses can be toggled with `show_update`.

## Installation
To add it on to your glance config, you'd want something like the following
```yaml
services:
  glance:
    ...
    links:
        - "tailscale:tailscale"

  tailscale:
    image: ghcr.io/fifty-six/glance.tailscale
    env-file: .env
    
```
with `TS_AUTH_KEY` in a `.env` file.

You can then use the url `https://tailscale/` as the extension url with a config like
```yaml
        - type: extension
          url: http://tailscale:8000
          allow-potentially-dangerous-html: true
          cache: 5m
        # optionally, with the defaults provided here
        # parameters:
        #    show_status: true
        #    show_update: false
```
