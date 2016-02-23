from select import select

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from dwebsocket.decorators import accept_websocket

from .models import Task
from .handler import handler


def index(request):
    return render_to_response('index.html', {

    }, context_instance=RequestContext(request))


@accept_websocket
def channel(request):
    if request.is_websocket:
        client = handler.register(request.websocket)
        for message in client:
            if not message:
                break

            client.request(message)

        handler.unregister(client)