from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer


def get_user_obj(request):
    token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
    data = {'token': token}
    valid_data = VerifyJSONWebTokenSerializer().validate(data)
    user = valid_data['user']

    return user