import os
import pytest
import sys
import uuid
from typing import Optional
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))
import lib.ansible as ansible  # noqa: E402


@pytest.mark.parametrize(
    "text,add,remove,expected",
    [
        ("text", True, False, "!vault |\ntext"),
        ("!vault |\ntext", True, False, "!vault |\ntext"),
        ("!vault |\ntext", False, True, "text"),
        ("text", False, True, "text")
    ],
)
def test_vault_yaml_tag(text: str, add: bool, remove: bool, expected: str):
    assert ansible.vault_yaml_tag(text, add, remove) == expected


@pytest.mark.parametrize(
    "directory,mock",
    [
        (str(uuid.uuid4()), False),
        (str(uuid.uuid4()), True),
    ],
)
def test_find_cfg_file(directory: str, mock: bool):
    if not mock:
        assert ansible.find_cfg_file([directory]) is None
    else:
        real_directory = '/tmp/' + directory
        ansible_cfg_path = real_directory + '/ansible.cfg'
        os.mkdir(real_directory)
        open(ansible_cfg_path, 'a').close()
        assert ansible.find_cfg_file([real_directory]) == ansible_cfg_path


@pytest.mark.parametrize(
    "directory,create,mock_config,mock_password",
    [
        (str(uuid.uuid4()), False, False, False),
        (str(uuid.uuid4()), True, False, False),
        (str(uuid.uuid4()), True, True, False),
        (str(uuid.uuid4()), True, True, True),
    ],
)
def test_cfg_file_vault_password(directory: str, create: bool, mock_config: bool, mock_password: bool):
    if create:

        real_directory = '/tmp/' + directory
        ansible_cfg_path = real_directory + '/ansible.cfg'
        password_file = real_directory + '/' + directory

        os.mkdir(real_directory)

        f = open(ansible_cfg_path, 'a')

        if mock_config:
            f.write("[defaults]\nvault_password_file=%s\n" % password_file)

        f.close()

        if mock_password:
            f = open(password_file, 'a')
            f.write("some_secure_vault_password\n")
            f.close()

        if create and mock_config and mock_password:
            assert ansible.cfg_file_vault_password(ansible_cfg_path) == "some_secure_vault_password"
        else:
            assert ansible.cfg_file_vault_password(ansible_cfg_path) is None


@pytest.mark.parametrize(
    "directory,create,mock_config,mock_password",
    [
        (str(uuid.uuid4()), False, False, False),
        (str(uuid.uuid4()), True, False, False),
        (str(uuid.uuid4()), True, True, False),
        (str(uuid.uuid4()), True, True, True),
    ],
)
def test_cfg_file_vault_ids(directory: str, create: bool, mock_config: bool, mock_password: bool):
    if create:

        real_directory = '/tmp/' + directory
        ansible_cfg_path = real_directory + '/ansible.cfg'
        password_file = real_directory + '/' + directory

        os.mkdir(real_directory)

        f = open(ansible_cfg_path, 'a')

        if mock_config:
            f.write("[defaults]\nvault_identity_list=%s@%s\n" % (directory, password_file))

        f.close()

        if mock_password:
            f = open(password_file, 'a')
            f.write("some_secure_vault_password\n")
            f.close()

        if create and mock_config and mock_password:
            assert ansible.cfg_file_vault_ids(ansible_cfg_path) == [(directory, "some_secure_vault_password")]
        else:
            assert ansible.cfg_file_vault_ids(ansible_cfg_path) is None


@pytest.mark.parametrize(
    "encrypted_text,password,expected",
    [
        ("""$ANSIBLE_VAULT;1.2;AES256;foo
37383462326432363533626462336535366665663731633630323566666533353132666632313135
3830633533646233393537663762343739616463326564620a323334613836346537306535616232
39346236376338316466373236663136306234386465376431633335613839306336623666663765
3265366331363933310a336130363031396364656461303264613733326566646663343032633934
3564""", "bar", "foo"),
        ("""$ANSIBLE_VAULT;1.1;AES256
34386330316561636165353438616539333835396431373866303733653366616639353732356362
3234346234616532633637343362623234353033366637350a613739623163376364333465636338
32313762343232396333346361353261643265373435336136383263376466663135366135613334
3732663334626132630a613932323939643636623636343866663334656263306265616433663834
3962""", "bar", "foo"),
    ],
)
def test_decrypt(encrypted_text: str, password: str, expected: str):
    assert ansible.decrypt(encrypted_text, password) == expected


@pytest.mark.parametrize(
    "text,password,vault_id",
    [
        ("foo", "bar", None),
        ("foo", "bar", "foo"),
    ],
)
def test_encrypt(text: str, password: str, vault_id: Optional[str]):
    encrypted_text = ansible.encrypt(text, password, vault_id)
    if vault_id is not None:
        assert ';' + vault_id in encrypted_text
    assert ansible.decrypt(encrypted_text, password) == text
