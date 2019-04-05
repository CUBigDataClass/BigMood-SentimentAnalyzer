import os
from Aggregator import Aggregator


path = os.path.join(os.path.curdir,'data/worldcities.csv')
aggregator = Aggregator(path)
assert 'united states' == aggregator.get_country('New York'), "Failed"
assert 'united states' == aggregator.get_country('New york'), "Failed"
assert None == aggregator.get_country(' york'), "Failed"

assert 'colorado' == aggregator.get_state('Denver'), "Failed"
assert 'california' == aggregator.get_state('palo alto'), "Failed"

assert 'united states' == aggregator.get_state_country('colorado'), "Failed"
assert 'united states' == aggregator.get_state_country('california'), "Failed"