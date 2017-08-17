from marshmallow import Serializer, fields

class FavcolorSerializer(Serializer):

    class Meta:
        fields = ("id", "color")

class UserSerializer(Serializer):

    colors = fields.Nested(FavcolorSerializer)

    class Meta:
        fields = ("id", "name", "gender", "age", "email", "about_me",
                  "address", "favbook_id", "survey_completed")

'''
class FavbookSerializer(Serializer):
    users = fields.Nested(UserSerializer)

    class Meta:
        fields = ("id", "title", "author", "users")
'''