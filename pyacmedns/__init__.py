"""
Client library for handling acme-dns communication and persistent account
storage.
"""

import json
import os

import requests

from pyacmedns.exceptions import AcmeDnsClientException, AcmeDnsStorageException

class Client(object):
    """
    Client class for handling communication with the acme-dns instance.

    :ivar acmedns_url: URL of acme-dns instance
    :type acmedns_url: str
    """

    def __init__(self, acmedns_url):
        """
        Initializes the acme-dns Client instance.

        :param str acmedns_url: URL of acme-dns instance

        """
        self.acmedns_url = acmedns_url

    def register_account(self, allowfrom):
        """
        Registers a new acme-dns account.

        :param list allowfrom: List of CIDR ranges to whitelist for TXT record
            updates.

        :returns: An acme-dns account dictionary.
        :rtype: dict

        :raises AcmeDnsClientException: When there's a communication error
            with the acme-dns instance.
        """

        if allowfrom:
            # Include whitelisted networks to the registration call
            reg_data = {"allowfrom": allowfrom}
            res = requests.post(self.acmedns_url+"/register",
                                data=json.dumps(reg_data))
        else:
            res = requests.post(self.acmedns_url+"/register")
        if res.status_code == 201:
            # The request was successful
            return res.json()
        else:
            # Encountered an error
            msg = ("Encountered an error while trying to register a new acme-dns "
                   "account. HTTP status {}, Response body: {}")
            raise AcmeDnsClientException(msg.format(res.status_code, res.text))

    def update_txt_record(self, account, txt):
        """
        Updates the TXT challenge record to acme-dns subdomain pointed by the
        account dictionary.

        :param dict account: Acme-dns account dictionary
        :param str txt: The validation token. Currently acme-dns requires this
            to be exactly 43 characters long.

        :raises AcmeDnsClientException: When there's a communication error
            with the acme-dns instance.

        """
        update = {"subdomain": account['subdomain'], "txt": txt}
        headers = {"X-Api-User": account['username'],
                   "X-Api-Key": account['password'],
                   "Content-Type": "application/json"}
        res = requests.post(self.acmedns_url+"/update",
                            headers=headers,
                            data=json.dumps(update))
        if res.status_code == 200:
            # Successful update
            return
        else:
            msg = ("Encountered an error while trying to update TXT record in "
                   "acme-dns. \n"
                   "------- Request headers:\n{}\n"
                   "------- Request body:\n{}\n"
                   "------- Response HTTP status: {}\n"
                   "------- Response body: {}")
            s_headers = json.dumps(headers, indent=2, sort_keys=True)
            s_update = json.dumps(update, indent=2, sort_keys=True)
            s_body = json.dumps(res.json(), indent=2, sort_keys=True)
            raise AcmeDnsClientException(msg.format(s_headers, s_update,
                                                    res.status_code, s_body))


class Storage(object):
    """
    Client class for handling communication with the acme-dns instance.

    :ivar storagepath: Path of the persistent account storage.
    :type storagepath: str

    :ivar permission: If the storage file does not exist yet, the filesystem
        permissions to apply to the newly created file. Often expressed as an
        octal number (base 8) in *nixes.
    :type permission: int

    """
    def __init__(self, storagepath, permission=0o600):
        """
        Initializes the acme-dns Storage instance.

        :param str storagepath: Path of the persistent account storage.
        :param int permission: Filesystem permissions for the persistent storage
            file.

        """
        self.storagepath = storagepath
        self.permission = permission
        self._data = self.load()

    def load(self):
        """
        Reads the storage content from the disk.

        :returns: The persistent account storage content.
        :rtype: dict

        :raises AcmeDnsStorageException: When there's an error loading the data.

        """
        data = dict()
        filedata = ""
        try:
            with open(self.storagepath, 'r') as fh:
                filedata = fh.read()
        except IOError as e:
            if os.path.isfile(self.storagepath):
                # Only error out if file exists, but cannot be read
                raise AcmeDnsStorageException(
                    "Storage file exists but cannot be read")
        try:
            data = json.loads(filedata)
        except ValueError:
            if len(filedata) > 0:
                # Storage file is corrupted
                raise AcmeDnsStorageException("Storage JSON is corrupted")
        return data

    def save(self):
        """
        Saves the storage content to disk

        :raises AcmeDnsStorageException: When there's an error writing the data.
        """
        serialized = json.dumps(self._data)
        try:
            with os.fdopen(os.open(self.storagepath,
                                   os.O_WRONLY | os.O_CREAT,
                                   self.permission), 'w') as fh:
                fh.truncate()
                fh.write(serialized)
        except IOError as e:
            raise AcmeDnsStorageException("Could not write storage file.")
        except OSError as e:
            raise AcmeDnsStorageException(e)

    def put(self, domain, destination):
        """
        Put the original domain to the acme-dns subdomain destination to the
        storage object and sanitize it in case of wildcards.

        :param str domain: The domain that is being validated
        :param str destination: The acme-dns domain that the CNAME points to.

        """
        # If wildcard domain, remove the wildcard part as this will use the
        # same validation record name as the base domain
        if domain.startswith("*."):
            domain = domain[2:]
        self._data[domain] = destination

    def fetch(self, domain):
        """
        Fetches the CNAME destination for a domain from the storage dict

        :param str domain: Domain to fetch the associated CNAME destination of.

        :returns: Associated acme-dns subdomain
        :rtype: str or None

        """
        try:
            return self._data[domain]
        except KeyError:
            return None
