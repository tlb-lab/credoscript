import os
import re
import functools
import json
from urllib import unquote
from urlparse import parse_qs

import werkzeug
from werkzeug import Request
from werkzeug import Response
from werkzeug import redirect

# http://www.sfsu.edu/training/mimetype.htm
BIN  = 'application/octet-stream'
JSON = 'application/json'
TEXT = 'text/plain'
HTML = 'text/html'
XML  = 'text/xml'
JS   = 'application/javascript'
ATOM = 'application/atom+xml'
ICON = 'image/vnd.microsoft.icon'
PDF  = 'application/pdf'
RTF  = 'application/rtf'
PNG  = 'image/png'

JQUERY_TYPES = {}
JQUERY_TYPES[JSON] = 'json'
JQUERY_TYPES[TEXT] = 'text'
JQUERY_TYPES[HTML] = 'html'
JQUERY_TYPES[XML]  = 'xml'

def generate_route_decorator(method):
    '''
    returns a decorator that will add Route objects to method
    '''
    def decorator(self, pattern, accepts=None, produces=JSON, has_payload=False, transform_body=None):
        '''
        the decorator to register a new Route
        '''
        def wrapper(func):
            '''
            the decorator itself
            '''
            self.register_route(method, pattern, func, accepts, produces, has_payload, transform_body)
            
            return func
        
        return wrapper
    
    return decorator

class Route(object):
    '''
    a class that represents a registered route
    '''
    def __init__(self, pattern, application, accepts=None, produces=TEXT,
                 has_payload=False, transform_body=None):
        '''
        pattern -- the regex that when matches calls application
        application -- the method to call when pattern matches
        accepts -- the content type that is accepted
        produces -- the content type that application produces
        has_payload -- if the request contains information on the body
        transform_body -- if accepts is JSON then call the method in this
            attribute and use the returned value as parameter to the method that
            handles the request
        '''
        self.pattern = pattern
        self.regex = re.compile(pattern)
        self.group_count = pattern.count('(')
        self.application = application
        self.accepts = accepts
        self.produces = produces
        self.has_payload = has_payload
        self.transform_body = transform_body

class Application(object):
    '''application for requests'''
    __name__ = 'tubes'

    def __init__(self):
        self.routes = {}
        self.marshallers = {JSON: json.dumps}
        self.static_paths = {}

    def __call__(self, environ, start_response):
        '''
        try to match the request with the registered routes
        '''
        path = environ.get('PATH_INFO', '')
        command = environ.get('REQUEST_METHOD', None)
        qstring = environ.get('QUERY_STRING', None)
        
        request = Request(environ)

        for route in self.routes.get(command, ()):
            accepts = request.accept_mimetypes.values()
            
            if route.accepts and request.accept_mimetypes and \
                    route.accepts not in accepts and  '*/*' not in accepts:
                continue

            match = route.regex.match(path)

            if match is not None:
                
                # ARGUMENTS THAT ARE GOING TO BE RETURNED BY THE DECORATOR
                if route.group_count == 0: args = []
                elif route.group_count == 1: args = [match.group(1)]
                else: args = match.group(*range(1, route.group_count + 1))

                # CHANGE THIS HERE TO MODIFY POST METHOD
                if route.accepts == JSON:
                    data = json.loads(request.stream.read())

                    if route.transform_body is not None:
                        data = route.transform_body(data)

                    # ADD THE BODY OF THE REQUEST AS FIRST PARAMETER
                    args.insert(0, data)

                # PARSE AND UNQUOTE QUERY STRING
                if qstring:
                    params = parse_qs(qstring)
                    
                    # VALUES QUERY STRINGS ARE ALWAYS LISTS
                    for key,values in params.items():
                        params[key] = [unquote(value) for value in values]
                    
                else: params = {}

                # PARAMETERS THAT ARE GOING TO BE RETURNED TO THE DECORATED FUNCTION
                kwargs = {'args': args, 'params': params}

                try: result = route.application(request, **kwargs)
                except Response, response: return response

                if isinstance(result, werkzeug.BaseResponse):
                    return result(environ, start_response)
                
                # CONVERTS THE RESULT INTO THE SELECTED TYPE
                elif route.produces in self.marshallers:
                    result = self.marshallers[route.produces](result)

                return Response(result, content_type=route.produces)(environ, start_response)

        return Response(status=404)(environ, start_response)

    def register_route(self, method, pattern, application, accepts, produces,
                       has_payload, transform_body):
        '''
        register a new route on the routes class variable
        '''
        if method not in self.routes: self.routes[method] = []

        self.routes[method].append(Route(pattern, application, accepts, produces, has_payload, transform_body))

    def register_marshaller(self, mimetype, func):
        '''
        register a method to transform an input to an output accourding
        to the mimetype
        '''
        self.marshallers[mimetype] = func

    def register_static_path(self, match_path, *dest_path):
        '''register a path that will be served as static content'''
        self.static_paths[match_path] = os.path.join(*dest_path)

    def authorize(self, authorize_func):
        '''decorator to validate a request prior to calling the application
        if the authorize_func returns True, them the function is called
        otherwise 401 is returned
        '''
        def wrapper(func):
            @functools.wraps(func)
            def inner(*args, **kwargs):
                if authorize_func(args[0]): return func(*args, **kwargs)
                else: return Response("unauthorized", 401)

            return inner
        
        return wrapper

    # http://tools.ietf.org/html/rfc2616#page-51
    get = generate_route_decorator('GET')
    post = generate_route_decorator('POST')
    put = generate_route_decorator('PUT')
    delete = generate_route_decorator('DELETE')
    options = generate_route_decorator('OPTIONS')
    head = generate_route_decorator('HEAD')
    trace = generate_route_decorator('TRACE')
    connect = generate_route_decorator('CONNECT')

def run(application, **kwargs):
    '''
    create a server instance and run it
    '''
    host = kwargs.get('host', '0.0.0.0')
    port = kwargs.get('port', 8000)
    reload = kwargs.get('reload', False)
    debug = kwargs.get('debug', False)
    use_evalex = kwargs.get('use_evalex', True)
    extra_files = kwargs.get('extra_files', None)
    reload_interval = kwargs.get('reload_interval', 1)
    threaded = kwargs.get('threaded', False)
    processes = kwargs.get('processes', 1)
    request_application = kwargs.get('request_application', None)
    passthrough_errors = kwargs.get('passthrough_errors', False)
    
    werkzeug.run_simple(host, port, application, reload, debug, use_evalex, extra_files,
                        reload_interval, threaded, processes, request_application,
                        application.static_paths, passthrough_errors)