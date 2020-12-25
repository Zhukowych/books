from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import Categories, Book
from .schema import schema
from django.conf import settings


class Util:

    @staticmethod
    def create_full_url_of_book_image_and_files(books: tuple):
        for book in books:
            for file in book['referencedBookFile']:
                file['file'] = settings.STANDARD_IP + settings.MEDIA_URL + file['file']
            book['image'] = settings.STANDARD_IP + settings.MEDIA_URL + book['image']['imageLink']

    @staticmethod
    def resolve_books_list(books: tuple):
        for book in range(len(books)):
            books[book] = books[book]['book']


class DataQuery:

    @staticmethod
    def get_all_public_and_users_books(user_id: int) -> tuple:
        query = '''
            query get_all_books($userId: Int!){
                books(userId:$userId){
                    id,
                    title,
                    referencedBookFile{
                        file,
                        expansion
                    },
                    image{
                        imageLink
                    },
                    category{ 
                        id,
                        name
                    },
                    uploadAuthor{
                        id
                    }
                }
            }    
        '''
        result = schema.execute(query, variables={"userId": user_id}).data['books']
        Util.create_full_url_of_book_image_and_files(result)
        return result

    @staticmethod
    def get_my_books(user_id: int) -> tuple:
        query = '''
            query get_my_books($userId: Int!){
                myBooks(userId: $userId){
                    id,
                    title,
                    referencedBookFile{
                        file,
                        expansion
                    },
                    image{
                        imageLink
                    },
                    category{ 
                        id,
                        name
                    },
                    uploadAuthor{
                        id
                    }
                }
            }
        '''
        result = schema.execute(query, variables={'userId': user_id}).data["myBooks"]
        Util.create_full_url_of_book_image_and_files(result)
        return result

    @staticmethod
    def get_category_books_and_children_categories(user_id: int, category_id: int) -> tuple:
        category = get_object_or_404(Categories, id=category_id)
        query = '''
            query get_category_books($categoryId: Int!, $userId: Int!){
                booksFromCategory(userId: $userId, categoryId: $categoryId){
                    id,
                    title,
                    referencedBookFile{
                        file,
                        expansion
                    },
                    image{
                        imageLink
                    },
                    category{ 
                        id,
                        name
                    },
                    uploadAuthor{
                        id
                    }
                },
                childrenCategories(categoryId: $categoryId){
                    id,
                    name
                }
            }
        '''
        result = schema.execute(query, variables={'categoryId': category_id, "userId": user_id}).data
        Util.create_full_url_of_book_image_and_files(result['booksFromCategory'])
        result['category'] = {"name": category.name, "id": category_id}
        return result

    @staticmethod
    def get_favorite_books(user_id: int) -> tuple:
        query = '''
            query get_my_books($userId: Int!){
                favoriteBooks(userId: $userId){
                    book{
                        id,
                        title,
                        referencedBookFile{
                            file,
                            expansion
                        },
                        image{
                            imageLink
                        },
                        category{ 
                            id,
                            name
                        },
                        uploadAuthor{
                            id
                        }
                    }
                }
            }
        '''
        result = schema.execute(query, variables={"userId": user_id}).data['favoriteBooks']
        Util.resolve_books_list(result)
        Util.create_full_url_of_book_image_and_files(result)
        return result

    @staticmethod
    def create_book(data: tuple, user_id: int, category_id: int, book_image_id: int) -> int:
        query = '''
            mutation createBookMutation($title: String!, $translator: String!, $series: String!, $countOfPages: Int!,
                $language: String!, $edition: String!, $uploadAuthorId: Int!, $author: String!, $categoryId: Int!,
                $description: String!, $imageId: Int!, $isPublic: Boolean!){
                createBook(bookInput:{
                    title: $title, translator: $translator, series: $series, countOfPages: $countOfPages,
                     language: $language, edition: $edition, uploadAuthorId: $uploadAuthorId, author: $author, 
                     categoryId: $categoryId, description: $description, imageId: $imageId, isPublic: $isPublic 
                }){
                    book{
                        id
                    }
                }
            }
        '''
        all_book_data = {**data, **{"categoryId": category_id, "imageId": book_image_id, "uploadAuthorId": user_id}}
        result = schema.execute(query, variables=all_book_data)
        return int(result.data["createBook"]['book']['id'])

    @staticmethod
    def move_book_files_from_buffer_to_vault(user_id: int, book_id: int) -> None:
        query = '''
            mutation move_book_files_from_buffer_to_vault($userId: Int!, $bookId: Int!){
                moveBookFilesFromBufferToVault(userId: $userId, bookId: $bookId){
                    book{
                        id
                    }
                }
            }
        '''
        result = schema.execute(query, variables={"userId": user_id, "bookId": book_id})

    @staticmethod
    def upload_book_image_link(image: InMemoryUploadedFile) -> int:
        query = '''
            mutation upload_book_image_link($image: Upload){
                uploadBookImageLink(image: $image){
                    imageLink{
                        id
                    }
                }
            }
        '''
        result = schema.execute(query, variables={"image": image})
        print(result)
