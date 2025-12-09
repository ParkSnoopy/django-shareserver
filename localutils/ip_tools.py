

# request: Django HttpRequest Object

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_ranged_ip(request, start=0, end=2, mask='#'):
    ip = get_client_ip(request)

    return (f'{mask}.'*start)+'.'.join(ip.split('.')[start:end])+(f'.{mask}'*(4-end))
