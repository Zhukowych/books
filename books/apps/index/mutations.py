from graphene_file_upload.scalars import Upload
import graphene
from .types import BookType, Book, BufferFiles, BookFiles, BookImageLinkType, BookImageLink
from django.utils import timezone


class BookInput(graphene.InputObjectType):
    id = graphene.ID()
    title = graphene.String()
    translator = graphene.String()
    series = graphene.String()
    count_of_pages = graphene.Int()
    language = graphene.String()
    edition = graphene.String()
    upload_author_id = graphene.Int()
    author = graphene.String()
    category_id = graphene.Int()
    description = graphene.String()
    image_id = graphene.Int()
    is_public = graphene.Boolean()


class CreateBook(graphene.Mutation):
    class Arguments:
        book_input = BookInput(required=True)

    ok = graphene.Boolean()
    book = graphene.Field(BookType)

    @staticmethod
    def mutate(self, info, book_input=None):
        ok = True
        book_instance = Book.objects.create(
            title=book_input.title,
            translator=book_input.translator,
            series=book_input.series,
            count_of_pages=book_input.count_of_pages,
            language=book_input.language,
            edition=book_input.edition,
            upload_author_id=book_input.upload_author_id,
            author=book_input.author,
            category_id=book_input.category_id,
            description=book_input.description,
            date_uploaded=timezone.now(),
            image_id=book_input.image_id,
            is_public=book_input.is_public
        )
        return CreateBook(ok=ok, book=book_instance)


class MoveFilesFromBufferToVault(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int()
        book_id = graphene.Int()

    ok = graphene.Boolean()
    book = graphene.Field(BookType)

    @staticmethod
    def mutate(self, info, user_id, book_id):
        ok = True
        buffer = BufferFiles.objects.filter(user__id=user_id)
        for element in buffer:
            BookFiles.objects.create(book_id=book_id, file=element.file, expansion=element.file.name.split('.')[-1])
        buffer.delete()
        return MoveFilesFromBufferToVault(ok=ok, book=Book.objects.get(id=book_id))


class UploadBookImageLink(graphene.Mutation):
    class Arguments:
        image = Upload()

    ok = graphene.Boolean()
    image_link = graphene.Field(BookImageLinkType)

    @staticmethod
    def mutate(self, info, image):
        ok = True
        image_link_instance = BookImageLink.objects.create(image_link=image)
        return UploadBookImageLink(ok=ok, image_link=image_link_instance)


class Mutation(graphene.ObjectType):
    create_book = CreateBook.Field()
    move_book_files_from_buffer_to_vault = MoveFilesFromBufferToVault.Field()
    upload_book_image_link = UploadBookImageLink.Field()
