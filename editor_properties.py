import sys
import os
import json

class EditorProperties():
    """

    :param config_filename: (str) name of a .smg Smeagol configuration file
    """
    def __init__(self, config_filename=None):
        os.chdir(os.path.dirname(sys.argv[0]))
        with open('editor_properties.json') as template:
            self.template = json.load(template)
        try:
            with open(config_filename) as config:
                self.config = json.load(config)
        except TypeError:
            self.config = ''

    

    def make_site_from_config(self, config):
        details = {}
        properties = config.splitlines()
        for property_ in properties:
            with ignored(ValueError):
                key, value = property_.split(': ')
                details[key] = value
        files = dict(source='source', template='template', markdown='markdown',
            searchjson='searchjson')
        for file_ in files.keys():
            with ignored(KeyError):
                files[file_] = details.pop(file_)
                details['files'] = Files(**files)
        return details

    def get_linkadder_from_config(self, config):
        """
        Create an AddRemoveLinks instance based on a given configuration file

        :param config: (str) The appropriate section of a configuration file
        """
        properties = config.splitlines()
        possible_adders = filter(lambda x: x.owner not in ['site', 'file'], properties_window)
        link_adders = []
        for property_ in properties:
            config_adder = property_.split(': ')
            link_adders.append(self.create_linkadder(possible_adders, config_adder))
        return link_adders

    def create_linkadder(self, possible_adders, config_adder):
        """
        Create an instance of a Link Adder

        :param possible_adders: (Property[]) the editor properties that
        correspond to LinkAdders
        :param config_adder: (tuple) a (key, value) pair from a config. file
        """
        try:
            key, value = config_adder
        except ValueError:
            (key, ), value = config_adder, None
        adder = filter(lambda x: x.property == key, possible_adders)
        adder = adder[0].owner() if value is None else adder[0].owner(value)
        return adder
