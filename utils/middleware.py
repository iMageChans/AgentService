class SwaggerFixMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 处理 Swagger UI 的请求
        if request.path.startswith('/swagger') or request.path.startswith('/redoc'):
            # 修改请求的 PATH_INFO，移除 FORCE_SCRIPT_NAME
            script_name = getattr(request, 'script_name', '')
            if script_name and request.path.startswith(script_name):
                request.path_info = request.path_info[len(script_name):]
        
        response = self.get_response(request)
        return response 