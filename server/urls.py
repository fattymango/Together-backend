"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import asyncio

from django.http import StreamingHttpResponse
from django.urls import path


def gen_message(msg):
    return f'data: {msg} '


async def iterator():
    async for i in range(100000):
        await asyncio.sleep(1)
        yield gen_message(f'iteration {i}')


def test_stream(request):
    stream = iterator()

    return StreamingHttpResponse(stream, status=200, content_type='text/event-stream')


def a_streaming_view(request):
    async def response_content():
        async for i in range(1, 6):
            await asyncio.sleep(1)
            yield f"Chunk {i}\n"

    return StreamingHttpResponse(response_content())


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('request/', include('request.urls')),
    path('location/', include('location.urls')),
    path('chat/', include('chat.urls')),
    path('report/', include('report.urls')),
    path('', include('myadmin.urls')),
    path('a-streaming-view/', test_stream)
]
