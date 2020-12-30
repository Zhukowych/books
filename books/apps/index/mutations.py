from graphene_file_upload.scalars import Upload
import graphene
from .types import BookType, Book, BufferFiles, BookFiles, BookImageLinkType, BookImageLink, CategoriesType, Categories, \
    Info, BookRating, CategoryRating
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


class EditBookData(graphene.Mutation):
    class Arguments:
        book_id = graphene.Int()
        book_input = BookInput(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(self, info, book_id, book_input):
        ok = True
        book_instance = Book.objects.get(id=book_id)
        book_instance.title = book_input.title
        book_instance.translator = book_input.translator
        book_instance.series = book_input.series
        book_instance.count_of_pages = book_input.count_of_pages
        book_instance.language = book_input.language
        book_instance.edition = book_input.edition
        book_instance.author = book_input.author
        book_instance.category.id = book_input.category_id
        book_instance.description = book_input.description
        book_instance.is_public = book_input.is_public
        if book_input.image_id != 0:
            book_instance.image.id = book_input.image_id
        book_instance.save()
        return EditBookData(ok=ok)


class ChangeBookVisibility(graphene.Mutation):
    class Arguments:
        book_id = graphene.Int()
        user_id = graphene.Int()
        reason = graphene.String()
        can_book_change_public = graphene.Boolean()

    ok = graphene.Boolean()

    @staticmethod
    def mutate(self, info, book_id, user_id, reason, can_book_change_public):
        ok = True
        book = Book.objects.get(id=book_id)
        if can_book_change_public:
            Info.objects.create(title="Повідомлення про заблокування книги під номером #", user_id=user_id,
                                book_id=book_id, messange=reason, type='u', answer_state='n')
            book.is_public = False
            book.can_change_public = False
            book.save()
        else:
            Info.objects.create(title="Повідомлення про розблокування книги під номером #", user_id=user_id,
                                book_id=book_id, messange=reason, type='u', answer_state='n')
            book.can_change_public = True
            book.save()
        return ChangeBookVisibility(ok=ok)


class DeleteBook(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int()
        book_id = graphene.Int()

    ok = graphene.Boolean()

    @staticmethod
    def mutate(self, info, user_id, book_id):
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return DeleteBook(ok=False)

        book.image.delete()
        BookFiles.objects.filter(book=book).delete()
        book.delete()
        return DeleteBook(ok=True)


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


class CreateCategory(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        parent_category_id = graphene.Int()

    ok = graphene.Boolean()
    category = graphene.Field(CategoriesType)

    @staticmethod
    def mutate(self, info, name, parent_category_id):
        ok = True
        category_instance = Categories.objects.create(name=name, parent_id=parent_category_id)
        return CreateCategory(ok=ok, category=category_instance)


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

class ChangeBookAndCategoryRating(graphene.Mutation):
    class Arguments:
        book_id = graphene.Int()
        category_id = graphene.Int()

    @staticmethod
    def mutate(self, info, book_id, category_id):
        try:
            br = BookRating.objects.get(book=book, user=request.user)
            cr = CategoryRating.objects.get(category=book.category, user=request.user)
        except:
            br = BookRating.objects.create(book=book, user=request.user, view=0)
            cr = CategoryRating.objects.create(category=book.category, user=request.user, view=0)
        cr.view = cr.view + 1
        br.view = br.view + 1
        br.save()
        cr.save()

class Mutation(graphene.ObjectType):
    create_book = CreateBook.Field()
    move_book_files_from_buffer_to_vault = MoveFilesFromBufferToVault.Field()
    create_category = CreateCategory.Field()
    upload_book_image_link = UploadBookImageLink.Field()
    edit_book_data = EditBookData.Field()
    change_book_visibility = ChangeBookVisibility.Field()
    delete_book = DeleteBook.Field()
