from marshmallow import Serializer, fields


class FavcolorSerializer(Serializer):

    class Meta:
        fields = ("id", "color")


class FavbookSerializer(Serializer):

    class Meta:
        fields = ("id", "title", "author")


class UserSerializer(Serializer):

    colors = fields.Nested(FavcolorSerializer, many=True)
    book = fields.Nested(FavbookSerializer)

    class Meta:
        fields = ("id", "name", "gender", "age", "email", "about_me",
                  "address", "book", "colors", "survey_completed")
