"""
horilla_middlewares.py

This module is used to register horilla's middlewares without affecting the horilla/settings.py
"""

import threading

from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render


class HealthCheckMiddleware:
    """
    Handle /health/ before SessionMiddleware and other layers that may touch
    the database or Redis. Load balancers (e.g. Railway) require a reliable 200.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.rstrip("/") == "health" and request.method in ("GET", "HEAD"):
            if request.method == "HEAD":
                return HttpResponse(status=200)
            return JsonResponse({"status": "ok"}, status=200)
        return self.get_response(request)

_thread_locals = threading.local()


class ThreadLocalMiddleware:
    """
    ThreadLocalMiddleWare
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response


class MethodNotAllowedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if isinstance(response, HttpResponseNotAllowed):
            return render(request, "405.html")
        return response


class SVGSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Apply security headers to SVG files
        if request.path.endswith(".svg") and response.status_code == 200:
            response["Content-Security-Policy"] = (
                "default-src 'none'; style-src 'unsafe-inline';"
            )
            response["X-Content-Type-Options"] = "nosniff"

        return response
