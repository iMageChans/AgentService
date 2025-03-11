import json
import os
import django
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PocketAi.settings")  # 替换为你的项目名称
django.setup()

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings
from django.http import JsonResponse


def fetch_user_info(request, token=None):
    try:
        response = fire(request=request, data={}, url='/api/users/me/', token=token)
        return response
    except requests.exceptions.RequestException as e:
        # 处理请求异常
        return {"error": str(e)}


def fire(request, data, url, token=None, method='get', content_type='json'):
    headers = {'Content-Type': 'application/json'}
    method = method.lower()

    if method not in ("post", "delete", "patch", "get", "put", "head"):
        raise ValueError(f"Unsupported HTTP method: {method}")

    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    if not token:
        token = (request.COOKIES.get(settings.TOKEN_COOKIE_NAME) or
                 request.headers.get('Authorization', ''))

    headers['Authorization'] = f'{token}'

    full_url = f"{settings.BASE_URL}{url}"
    kwargs = {'headers': headers}
    if method == 'get':
        kwargs['params'] = data
    else:
        if content_type == 'form':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            kwargs['data'] = data
        else:
            kwargs['json'] = data

    try:
        response = session.request(method, full_url, **kwargs)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {e} | URL: {full_url}")
        return wrapper_response({'error': '服务暂不可用'}, 503)

    result = {}
    if response.text:
        try:
            result = response.json()
            print(result)
        except ValueError:
            print(f"响应解析失败: {response.text}")
            result = {'error': '无效的响应格式'}

    # 记录日志（脱敏后）
    safe_data = data.copy()
    if 'password' in safe_data:
        safe_data['password'] = '******'
    print(f"请求: {method.upper()} {full_url} | 状态码: {response.status_code}")

    # 返回封装后的响应
    return wrapper_response(result, response.status_code)


def wrapper_response(data, status_code, headers=None):
    response = JsonResponse(data, status=status_code)
    if headers and 'X-New-Token' in headers:
        response.set_cookie(
            key=settings.TOKEN_COOKIE_NAME,
            value=headers['X-New-Token'],
            secure=True,
            httponly=True,
            samesite='Lax'
        )
    return response