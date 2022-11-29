import logging

from hansken_extraction_plugin.api.extraction_plugin import ExtractionPlugin
from hansken_extraction_plugin.api.plugin_info import Author, MaturityLevel, PluginId, PluginInfo
from hansken_extraction_plugin.runtime.extraction_plugin_runner import run_with_hanskenpy
from logbook import Logger
import json

log = Logger(__name__)


class Plugin(ExtractionPlugin):

    def plugin_info(self):
        plugin_info = PluginInfo(
            id=PluginId(domain='politie.nl', category='crypto', name='metamask-extractor'),
            version='1.0.0',
            description='This plugin extracts wallet addresses from Metamask mobile databases',
            author=Author('Benjamin Martens', 'benjamin.martens@politie.nl', 'Politie'),
            maturity=MaturityLevel.PROOF_OF_CONCEPT,
            webpage_url='',  # e.g. url to the code repository of your plugin
            matcher='persist-root AND $data.type=raw',  # add the query for the types of traces your plugin should match
            license='Apache License 2.0'
        )
        return plugin_info

    def process(self, trace, data_context):
        file = trace.open()
        # Store file contents in memory
        parsed_data = json.load(file)
        # Parse engine part as json
        engine_data = json.loads(parsed_data["engine"])
        # Get accounts
        accounts = engine_data['backgroundState']['AccountTrackerController']['accounts'].keys()

        if len(accounts) > 0:
            # Add metamask application
            application_trace = trace.child_builder()
            application_trace.update({
                'name': 'Metamask',
                'application.name': "Metamask",
            }).build()

            # Add found wallets
            for account in accounts:
                wallet_trace = application_trace.child_builder()
                wallet_trace.update({
                    "name" : account,
                    "cryptocurrencyWallet.type": "Metamask",
                    "cryptocurrencyWallet.misc": {"address": account}
                }).build()

        log.info(f"processing trace {trace.get('name')}")
        # Add your plugin implementation here


if __name__ == '__main__':
    # optional main method to run your plugin with Hansken.py
    # see detail at:
    #  https://netherlandsforensicinstitute.github.io/hansken-extraction-plugin-sdk-documentation/latest/dev/python/hanskenpy.html
    run_with_hanskenpy(Plugin,
                       endpoint='http://localhost:9091/gatekeeper/',
                       keystore='http://localhost:9090/kestore/',
                       project='ab73dccd-eea5-4025-8de8-670f3f2c5e5f')
