def success_response(data: dict, web):
    """Успешный ответ"""
    return web.json_response({'success': True, 'message': '', **data})


def error_response(message: str, web):
    """Не успешный ответ"""
    return web.json_response({'success': False, 'message': message})

