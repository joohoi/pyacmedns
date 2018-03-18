# pyacmedns 

A client library to handle [acme-dns](https://github.com/joohoi/acme-dns) client communication and persistent account storage. 

## Installation

Install from PyPI

`pip install pyacmedns`

## Usage

The following is a complete example of handling the validation using this library.

```python
#!/usr/bin/env python

from pyacmedns import Client, Storage

whitelisted_networks = ["192.168.11.0/24", "[::1]/128"] 
domain = "your.example.org"

# Initialize the client. Point it towards your acme-dns instance.
client = Client("https://auth.acme-dns.io")
# Initialize the storage. If the file does not exist, it will be 
# automatically created.
storage = Storage("/path/to/storage.json")

# Check if credentials were previously saved for your domain
account = storage.fetch("your.example.org")
if not account:
    # Account did not exist. Let's create a new one
    # The whitelisted networks parameter is optional
    account = client.register_account(whitelisted_networks) 
    # Save it
    storage.put(domain, account)
    storage.save()

# Update the acme-dns TXT record.
client.update_txt_record(account, "___validation_token_recieved_from_the_ca___") 
```

