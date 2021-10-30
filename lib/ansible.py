"""Functions that are specific to Ansible."""
import configparser
import os
from pathlib import Path
from ansible.config.manager import find_ini_config_file
from ansible.constants import DEFAULT_VAULT_ID_MATCH
from ansible.parsing.vault import VaultSecret, VaultLib
from typing import List, Optional, Tuple
from sublime_ansible_vault.lib.util import loop_last


def encrypt(text: str, password: str, vault_id: str = None):
    """Encrypt a string using the given password and optionally a Vault ID."""
    ansible_vault = VaultLib(secrets=[(DEFAULT_VAULT_ID_MATCH, VaultSecret(password.encode('utf-8')))])
    return (ansible_vault.encrypt(text, vault_id=vault_id).decode("utf-8"))


def decrypt(text: str, password: str) -> str:
    """Decrypt a string using the given password."""
    ansible_vault = VaultLib(secrets=[(DEFAULT_VAULT_ID_MATCH, VaultSecret(password.encode('utf-8')))])
    return ansible_vault.decrypt(text).decode('utf-8')


def find_cfg_file(dirs: List[str]) -> Optional[str]:
    """Look for ansible.cfg file in the usual directories + dirs. Returns None if not found."""
    for d in dirs:
        try:
            os.chdir(d)
        except OSError:
            continue
        cfg = find_ini_config_file()
        if cfg is not None:
            return cfg
    return None


def vault_yaml_tag(text: str, add=False, remove=False) -> str:
    """Add or remove the !vault tag to a text."""
    new_text = text
    if add:
        if "!vault" in text:
            return text
        new_text = "!vault |\n" + text

    elif remove:
        if "!vault" not in text:
            return text
        new_text = ""
        for last, line in loop_last(text.split('\n')):
            if "!vault" in line.strip():
                continue
            new_text = new_text + line.strip()
            if not last:
                new_text = new_text + '\n'
    return new_text


def cfg_file_vault_password(cfg: str) -> Optional[str]:
    """Return the contents of vault_password_file key if present and readable in cfg file."""
    config = configparser.ConfigParser()
    config.read(cfg)
    try:
        vault_password_file = config['defaults']['vault_password_file']
        return _get_file_content(vault_password_file)
    except KeyError:
        return None
    return None


def cfg_file_vault_ids(cfg: str) -> Optional[List[Tuple[str, str]]]:
    """Return a list of tuples with (tag, password) for each vault id in cfg file or None if no vault id present."""
    vault_ids = []
    config = configparser.ConfigParser()
    config.read(cfg)
    try:
        vault_identity_list = config['defaults']['vault_identity_list']
        for identity in vault_identity_list.split(','):
            tag, password_file = identity.split('@', 1)
            password_content = _get_file_content(password_file)
            if (password_content is not None and
                password_content != "" and
                tag is not None and
                tag != ""):  # noqa: E129
                vault_ids.append((tag, password_content))
    except KeyError:
        return None
    if len(vault_ids) == 0:
        return None
    return vault_ids


def _get_file_content(file: str) -> Optional[str]:
    """Return the content of a file or None if not valid."""
    if (os.path.isfile(file) and
        os.access(file, os.R_OK) and
        os.path.getsize(file)):  # noqa: E129
        return Path(file).read_text().rstrip()
    return None
