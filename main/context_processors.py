def my_custom_context_processor(request):
    return {
        'my_variable': 'hello',
        'user_ip': request.META['REMOTE_ADDR']
    }