import cProfile
import pstats
import io
from django.conf import settings

class ProfilerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            profiler = cProfile.Profile()
            profiler.enable()

            response = self.get_response(request)

            profiler.disable()
            s = io.StringIO()
            sortby = 'cumulative'
            ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
            ps.print_stats()

            print(s.getvalue())
        else:
            response = self.get_response(request)

        return response