import sublime
import sublime_plugin
import sys


class AnsibleVaultBase(sublime_plugin.TextCommand):
    def __init__(self, view) -> None:
        self.view = view
        self.ansible_cfg = None

        if self.view.window() is not None:
            if self.get_setting("site_packages_directory", default=None) is not None:
                sys.path.append(self.get_setting("site_packages_directory"))
                import sublime_ansible_vault.lib.ansible as ansible_imp  # noqa: E402
                import sublime_ansible_vault.lib.text as text_imp  # noqa: E402
                self.ansible = ansible_imp
                self.text = text_imp
            else:
                try:
                    # local dev sugar
                    import lib.ansible as ansible_imp  # noqa: E402
                    import lib.text as text_imp  # noqa: E402
                    self.ansible = ansible_imp
                    self.text = text_imp
                except Exception:
                    raise Exception("site_packages_directory not set")

            if self.get_setting("ansible_cfg", default=None) is not None:
                self.ansible_cfg = self.get_setting("ansible_cfg")
            else:
                self.ansible_cfg = self.ansible.find_cfg_file(self.view.window().folders())

    @property
    def vault_password(self):
        if self.ansible_cfg is not None:
            return self.ansible.cfg_file_vault_password(self.ansible_cfg)
        else:
            return None

    @property
    def vault_ids(self):
        if self.ansible_cfg is not None:
            return self.ansible.cfg_file_vault_ids(self.ansible_cfg)
        else:
            return None

    @property
    def is_selection(self) -> bool:
        selections = self.view.sel()
        if len(selections) == 1 and selections[0].a - selections[0].b == 0:
            return False
        return True

    def get_setting(self, key, default=None):
        settings = sublime.load_settings('VaultSavvy.sublime-settings')

        os_specific_settings = {}
        os_name = sublime.platform()
        if os_name == 'osx':
            os_specific_settings = sublime.load_settings('VaultSavvy (OSX).sublime-settings')
        elif os_name == 'windows':
            os_specific_settings = sublime.load_settings('VaultSavvy (Windows).sublime-settings')
        else:
            os_specific_settings = sublime.load_settings('VaultSavvy (Linux).sublime-settings')

        project_settings = self.view.window().project_data() or {}
        project_settings = project_settings.get('VaultSavvy', {})

        if project_settings.get(key) is not None and project_settings.get(key) != "":
            return project_settings.get(key)
        elif os_specific_settings.get(key) is not None and os_specific_settings.get(key) != "":
            return project_settings.get(key)
        elif settings.get(key) is not None and settings.get(key) != "":
            return settings.get(key)

        return default

    def padding_from_index(self, point_a):
        line = self.view.substr(self.view.line(point_a))
        return self.text.yaml_padding_from_line(line)

    def on_change(self, password):
        pass

    def on_cancel(self):
        pass


class AnsibleVaultOutputCommand(sublime_plugin.TextCommand):
    """Command to output the result."""
    def run(self, edit, selection=None, text=None):
        if text is not None:
            self.view.replace(edit, sublime.Region(selection[0], selection[1]), text)


class AnsibleVaultEncryptCommand(AnsibleVaultBase):

    def run(self, edit):

        if self.vault_password is not None:
            self.encrypt_with_password(self.vault_password)

        elif self.vault_ids is not None:
            ids = []
            for tup in self.vault_ids:
                ids.append(tup[0])
            self.view.window().show_quick_panel(ids, self.encrypt_with_vault_id)

        else:
            self.view.window().show_input_panel(
                'Password',
                '',
                self.encrypt_with_password,
                self.on_change,
                self.on_cancel)

    def encrypt_with_password(self, password):
        if password == -1:
            pass

        if(self.is_selection):
            for sel in self.view.sel():
                if sel.empty():
                    continue
                content = self.view.substr(sel)
                encrypted_text = self.ansible.encrypt(content, password)

                self.view.run_command(
                    'ansible_vault_output',
                    {
                        'text': self.ansible.vault_yaml_tag(
                            self.text.pad(
                                encrypted_text,
                                self.padding_from_index(sel.a)
                            ), add=True),
                        'selection': (sel.a, sel.b),
                    },
                )

    def encrypt_with_vault_id(self, id):
        if id == -1:
            pass

        vault_id, password = self.vault_ids[id]

        if(self.is_selection):
            for sel in self.view.sel():
                if sel.empty():
                    continue
                content = self.view.substr(sel)
                encrypted_text = self.ansible.encrypt(content, password, vault_id)

                self.view.run_command(
                    'ansible_vault_output',
                    {
                        'text': self.ansible.vault_yaml_tag(
                            self.text.pad(
                                encrypted_text,
                                self.padding_from_index(sel.a)
                            ), add=True),
                        'selection': (sel.a, sel.b),
                    },
                )


class AnsibleVaultDecryptCommand(AnsibleVaultBase):
    def run(self, edit):
        if self.vault_password is not None:
            self.decrypt_with_password()
        elif self.vault_ids is not None:
            self.decrypt_with_vault_id()

        else:
            self.view.window().show_input_panel(
                'Password',
                '',
                self.decrypt_with_password,
                self.on_change,
                self.on_cancel)

    def decrypt_with_password(self, password):
        if password == -1:
            pass

        if(self.is_selection):
            for sel in self.view.sel():
                if sel.empty():
                    continue
                content = self.text.unpad(self.ansible.vault_yaml_tag(self.view.substr(sel), remove=True))
                decrypted_text = self.ansible.decrypt(content, password)

                self.view.run_command('ansible_vault_output', {
                    'text': decrypted_text,
                    'selection': (sel.a, sel.b),
                })

    def decrypt_with_vault_id(self):
        if id == -1:
            pass

        if(self.is_selection):
            for sel in self.view.sel():
                if sel.empty():
                    continue
                content = self.text.unpad(self.ansible.vault_yaml_tag(self.view.substr(sel), remove=True))
                vault_id = content.split('\n')[0].split(';')[-1]
                for v in self.vault_ids:
                    if v[0] == vault_id:
                        decrypted_text = self.ansible.decrypt(content, v[1])
                        self.view.run_command('ansible_vault_output', {
                            'text': decrypted_text,
                            'selection': (sel.a, sel.b),
                        })
                        return
                self.view.window().show_input_panel(
                    'Password',
                    '',
                    self.decrypt_with_password,
                    self.on_change,
                    self.on_cancel)
