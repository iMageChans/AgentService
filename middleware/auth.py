# middleware/auth.py
import requests
from django.conf import settings
from django.http import JsonResponse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class TokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_api_url = f"{settings.BASE_URL.rstrip('/')}/users/api/users/me/"
        self.exempt_paths = [
            '/users/api/auth/login/',
            '/admin/',
            '/openapi.json'
        ]

    def __call__(self, request):
        if request.method == 'OPTIONS':
            return self.get_response(request)

        if self.should_authenticate(request):
            user_info = self.authenticate(request)
            if isinstance(user_info, JsonResponse):
                return user_info
            request.remote_user = user_info  # 注入用户对象

        return self.get_response(request)

    def should_authenticate(self, request):
        path = request.path_info
        return not any(path.startswith(exempt) for exempt in self.exempt_paths)

    def authenticate(self, request):
        token = self.extract_token(request)
        if not token:
            return JsonResponse({'detail': 'Missing credentials'}, status=401)

        session = requests.Session()
        retries = Retry(total=2, backoff_factor=0.1)
        session.mount('https://', HTTPAdapter(max_retries=retries))

        try:
            # 直接发送原始Token（无Bearer前缀）
            response = session.get(
                self.auth_api_url,
                headers={'Authorization': token},  # 关键修改点
                timeout=3
            )
            response.raise_for_status()
            return response.json().get('data', {})
        except requests.HTTPError as e:
            return JsonResponse(
                {'detail': 'Invalid token'},
                status=401 if e.response.status_code == 401 else 503
            )
        except requests.RequestException:
            return JsonResponse({'detail': 'Auth service error'}, status=503)

    def extract_token(self, request):
        """从请求中提取Token（不再处理Bearer前缀）"""
        raw_token = request.headers.get('Authorization', '')
        if raw_token:
            return raw_token.strip()
        return request.COOKIES.get(settings.TOKEN_COOKIE_NAME)