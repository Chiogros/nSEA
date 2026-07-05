"""(not) Safe Exam Addon - nSEA.

Its goal is to provide access
to Safe Exam Browser (SEB) exams
to not-supported OS, like GNU/Linux.

Official SEB documentation:
https://safeexambrowser.org/developer/seb-config-key.html
"""

import argparse
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import gzip
import io
import json
import xml.etree.ElementTree as ET
from collections import OrderedDict
from hashlib import sha256


def decrypt_password(data: bytes) -> bytes:
    _version: bytes = data[0:1]
    _options: bytes = data[1:2]
    salt: bytes = data[2:10]
    _hmac_salt: bytes = data[10:18]
    iv: bytes = data[18:34]

    hmac_len: int = 32
    hmac_start: int = len(data) - hmac_len
    enc_data: bytes = data[34:hmac_start]
    _hmac: bytes = data[hmac_start:]

    print("Config password: ", end="")
    passphrase: bytes = bytes(input(), encoding="utf-8")
    kdf: PBKDF2HMAC = PBKDF2HMAC(
        # Algorithm is specified in RNCryptor spec (used by SEB)
        algorithm=hashes.SHA1(),
        length=32,
        salt=salt,
        iterations=10_000,
    )
    enc_key: bytes = kdf.derive(passphrase)

    cipher_alg: CipherAlgorithm = algorithms.AES256(enc_key)
    cipher_mode: Mode = modes.CBC(iv)
    cipher: Cipher = Cipher(cipher_alg, cipher_mode)
    decryptor: CipherContext = cipher.decryptor()
    dec_data_gz: bytes = decryptor.update(enc_data) + decryptor.finalize()

    # As AES-CBC pads data to make blocks, padding bytes must be removed
    unpadder: PaddingContext = padding.PKCS7(128).unpadder()
    dec_data_gz_unpadded: bytes = unpadder.update(dec_data_gz) + unpadder.finalize()

    config: bytes = gzip.decompress(dec_data_gz_unpadded)
    return config


def get_config_from_gzip(compressed_content: bytes) -> bytes:
    config: bytes = bytes()
    plain_content: bytes = gzip.decompress(compressed_content)
    encryption_type: bytes = plain_content[0:4]

    match encryption_type:
        case b"pswd":
            config = decrypt_password(plain_content[4:])
        case _:
            pass

    return config


def get_plain_config(filename: str) -> io.BytesIO:
    gzip_magic: bytes = b"\x1f\x8b"

    with open(filename, "rb") as f:
        config: bytes = bytes()
        file_content: bytes = f.read()
        magic: bytes = file_content[0:2]

        is_gzip: bool = magic == gzip_magic
        if is_gzip:
            config = get_config_from_gzip(file_content)
        else:
            config = file_content

        if is_gzip:
            with open(filename + ".plain", "wb") as f:
                f.write(config)

        return io.BytesIO(config)


# The dumped JSON data strictly needs to contain
# neither whitespaces or newlines.
def json_dumps_without_whitespaces(data: dict) -> str:
    return json.dumps(data).replace(" ", "").replace("\n", "")


# Concatenate and hash parts to get
# the final, HTTP header hash.
def make_http_header_hash(url: str, config_hash: str) -> str:
    hasher = sha256()
    hasher.update(url.encode("utf-8"))
    hasher.update(config_hash.encode("utf-8"))
    return hasher.hexdigest()


# Handle script arguments.
# e.g.: get the SEB config filename
def parse_args() -> dict:
    description = """Provide the HTTP header needed to access Safe Exam Browser (SEB) exams.
See the README to learn more."""
    config_file_help = "SEB config file you can get from the exam webpage."

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("config_file.seb", help=config_file_help)

    return vars(parser.parse_args())


# Main function which transforms SEB XML config file in JSON
# and hash some parts to get the final Config Key hash,
# usable to access SEB quizs.
def seb_hash_from_config(filename: str) -> None:
    config: bytes = get_plain_config(filename)
    xml: ET.ElementTree = ET.parse(config)

    # Build an ordered dict from XML
    unordered_data: dict = seb_xml_to_dict(xml)
    data: OrderedDict = sort_elements(unordered_data)

    # Format then hash the JSON config
    json_str = json_dumps_without_whitespaces(data)
    config_hash = sha256(json_str.encode("utf-8")).hexdigest()

    # Build the header hash from the URL and the config hash
    url = data["startURL"]
    config_key = make_http_header_hash(url, config_hash)

    print(f"X-SafeExamBrowser-ConfigKeyHash: {config_key}")


# Transforms SEB XML config file to a
# dictionnary, containing corresponding key-values.
def seb_xml_to_dict(xml: ET.ElementTree) -> dict:
    data = {}
    # True when a <key> has been found,
    # meaning that the next tag is a value.
    value_on_next_elem = False
    # <key> value which will be inserted in data
    # once the value is fetched.
    key_text = ""

    # SEB config file is strangely set up.
    # XML tags hierarchy isn't recognized and
    # all tags are set at the root level.
    for elem in xml.iter():
        # A key-value pair is found.
        if elem.tag == "key":
            key_text = elem.text
            value_on_next_elem = True
            continue

        # We are looking for the associted key's value.
        if value_on_next_elem:
            value_on_next_elem = False
            match elem.tag:
                case "true":
                    data[key_text] = True
                case "false":
                    data[key_text] = False
                case "array":
                    data[key_text] = []
                case "string":
                    data[key_text] = elem.text
                case "integer":
                    data[key_text] = int(elem.text)

    return data


# The elements strictly need to be sorted
# case insensitively.
def sort_elements(data: dict) -> OrderedDict:
    ord_data = OrderedDict()

    # Sorting keys by lowering them all,
    # then inserting the key-values in the OrderedDict
    sorted_keys = sorted(data, key=lambda s: s.lower())
    for key in sorted_keys:
        ord_data[key] = data[key]

    return ord_data


if __name__ == "__main__":
    args = parse_args()
    seb_hash_from_config(args["config_file.seb"])
