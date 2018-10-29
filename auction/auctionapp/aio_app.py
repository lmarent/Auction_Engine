from aiohttp.web import Application, run_app

from settings import config
from aiohttp_rest import RestResource
from models import Bid
from sqlalchemy import engine_from_config


app = Application()
app['config'] = config
bid_resource = RestResource(collection_name='bids', factory=Bid, 
							properties=('code', 'created_at', 'created_by', 'quantity', 'price'), 
							id_field= 'code')

bid_resource.register(app.router)


if __name__ == '__main__':

    run_app(app)