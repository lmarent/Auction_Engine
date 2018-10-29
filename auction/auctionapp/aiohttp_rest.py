import inspect
import simplejson as json
from collections import OrderedDict
from models import Bid, session
from aiohttp.http_exceptions import  HttpBadRequest
from aiohttp.web_exceptions import HTTPMethodNotAllowed
from aiohttp.web import Request, Response
from aiohttp.web_urldispatcher import UrlDispatcher


__version__ = '0.1.0'


DEFAULT_METHODS = ('GET', 'POST', 'PUT', 'DELETE')


class RestEndpoint:

    def __init__(self):
        self.methods = {}

        for method_name in DEFAULT_METHODS:
            method = getattr(self, method_name.lower(), None)
            if method:
                self.register_method(method_name, method)

    def register_method(self, method_name, method):
        self.methods[method_name.upper()] = method

    async def dispatch(self, request: Request):
        """
        This is the method being called when the user sends the request
        """
        method = self.methods.get(request.method.upper())
        if not method:
            raise HTTPMethodNotAllowed('', DEFAULT_METHODS)

        wanted_args = list(inspect.signature(method).parameters.keys())
        available_args = request.match_info.copy()
        available_args.update({'request': request})

        unsatisfied_args = set(wanted_args) - set(available_args.keys())
        if unsatisfied_args:
            # Expected match info that doesn't exist
            raise HttpBadRequest('')

        return await method(**{arg_name: available_args[arg_name] for arg_name in wanted_args})


class CollectionEndpoint(RestEndpoint):
    """
    A collection endpoint represents a set of object's instance. For examplein a banking environment the collection
    is customers and instance endpoint is a particular customer
    """  
    def __init__(self, resource, collection_name,  factory, properties):
        super().__init__()
        self.resource = resource
        self.collection_name = collection_name
        self.factory = factory
        self.properties = properties

    async def get(self) -> Response:
        data = []

        instances = session.query(self.factory).all()
        for instance in instances:
            data.append(self.resource.render(instance))

        return Response ( status=200, body=self.resource.encode({
            self.collection_name : data
            }), content_type='application/json')


    async def post(self, request):
        data = await request.json()
        instance=self.factory(**data)
        session.add(instance)
        session.commit()

        return Response(status=201, body=self.resource.encode({
            self.collection_name : [
                
                    OrderedDict((key, getattr(instance, key)) for key in self.properties)

                    for instance in session.query(Bid)

                    ]
            }), content_type='application/json')


class InstanceEndpoint(RestEndpoint):
    """
    An instance endpoint represents an object's instance. For examplein a banking environment the collection
    is customers and instance endpoint is the particular customer
    """
    def __init__(self, resource, collection_name,  factory, properties):
        super().__init__()
        self.resource = resource
        self.collection_name = collection_name
        self.factory = factory
        self.properties = properties

    async def get(self, instance_id):
        instance = session.query(self.factory).filter(self.factory.id == instance_id).first()
        if not instance:
            return Response(status=404, body=json.dumps({'not found': 404}), content_type='application/json')
        data = self.resource.render_and_encode(instance)
        return Response(status=200, body=data, content_type='application/json')

    async def put(self, request, instance_id):
        print('in put')
        data = await request.json()

        instance = session.query(self.factory).filter(self.factory.id == instance_id).first()
        for key,value in data.items():
            setattr(instance,key,value)

        session.add(instance)
        session.commit()

        return Response(status=201, body=self.resource.render_and_encode(instance),
                        content_type='application/json')

    async def delete(self, instance_id):
        instance = session.query(self.factory).filter(self.factory.id == instance_id).first()
        if not instance:
            abort(404, message="{0} {1} doesn't exist".format(self.collection_name, id))
        session.delete(instance)
        session.commit()
        return Response(status=204)


class RestResource:
    def __init__(self, collection_name, factory, properties, id_field):
        self.collection_name = collection_name
        self.factory = factory
        self.properties = properties
        self.id_field = id_field

        self.collection_endpoint = CollectionEndpoint(self, self.collection_name, self.factory, self.properties)
        self.instance_endpoint = InstanceEndpoint(self, self.collection_name, self.factory, self.properties)

    def register(self, router: UrlDispatcher):
        router.add_route('*', '/{collection}'.format(collection=self.collection_name), self.collection_endpoint.dispatch)
        router.add_route('*', '/{collection}/{{instance_id}}'.format(collection=self.collection_name), self.instance_endpoint.dispatch)

    def render(self, instance):
        return OrderedDict((key, getattr(instance, key)) for key in self.properties)

    @staticmethod
    def encode(data):
        return json.dumps(data, indent=4).encode('utf-8')

    def render_and_encode(self, instance):
        return self.encode(self.render(instance))