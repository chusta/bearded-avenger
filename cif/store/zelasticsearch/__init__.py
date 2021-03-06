import logging
import os

from cif.store.plugin import Store
from cif.store.zelasticsearch.token import TokenMixin
from cif.store.zelasticsearch.indicator import IndicatorMixin
from elasticsearch_dsl.connections import connections
from cif.constants import TOKEN_CACHE_DELAY
import arrow
from cif.constants import PYVERSION

ES_NODES = os.getenv('CIF_ES_NODES', '127.0.0.1:9200')
TRACE = os.environ.get('CIF_STORE_ES_TRACE')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not TRACE:
    logger.setLevel(logging.ERROR)

    es_logger = logging.getLogger('elasticsearch')
    es_logger.propagate = False
    es_logger.setLevel(logging.ERROR)

    if PYVERSION == 2:
        urllib_logger = logging.getLogger('urllib2')
    else:
        urllib_logger = logging.getLogger('urllib3')
    urllib_logger.setLevel(logging.ERROR)


class _ElasticSearch(IndicatorMixin, TokenMixin, Store):
    # http://stackoverflow.com/questions/533631/what-is-a-mixin-and-why-are-they-useful

    name = 'elasticsearch'

    def __init__(self, nodes=ES_NODES, **kwargs):

        if type(nodes) == str:
            nodes = nodes.split(',')

        logger.info('setting es nodes {}'.format(nodes))
        connections.create_connection(hosts=nodes)

        self.token_cache = {}
        self.token_cache_check = arrow.utcnow().timestamp + TOKEN_CACHE_DELAY

    def ping(self, token):
        # http://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch.client.IndicesClient.stats
        x = connections.get_connection().cluster.health()

        if x['status'] in ['green', 'yellow']:
            return True

Plugin = _ElasticSearch
