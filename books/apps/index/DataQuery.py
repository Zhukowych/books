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

    @staticmethod
    def format_dict_for_updating_book(book_data: dict, edited_book_data: dict):
        del edited_book_data['image']
        edited_book_data["count_of_pages"] = edited_book_data.pop("countOfPages")
        edited_book_data["is_public"] = edited_book_data.pop("isPublic")
        del book_data['_state']

    """--DECORATORS--"""

    @staticmethod
    def check_image_to_none(function_to_decorate):
        def function_wrapper(image):
            if image:
                return function_to_decorate(image)
            else:
                return 0

        return function_wrapper


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
        print(result)
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
    def get_or_create_category_for_book(category_data: dict) -> int:
        category = category_data['category']
        query = '''
            mutation create_category($name: String!, $parent_category_id: Int!){
                createCategory(name: $name, parentCategoryId: $parent_category_id){
                    category{
                        id
                    }
                }
            }
        '''
        if category:
            return category.id
        else:
            result = schema.execute(query, variables={"name": category_data['name'],
                                                      "parent_category_id": category_data['parent_category'].id}).data
            return int(result['createCategory']['category']['id'])

    @staticmethod
    @Util.check_image_to_none
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
        result = schema.execute(query, variables={"image": image}).data
        return int(result['uploadBookImageLink']['imageLink']['id'])

    @staticmethod
    def edit_book(edited_book_data: dict, category_data: dict, book_id: int) -> None:
        query = '''
            mutation editBookData($Id: Int!, $title: String!, $translator: String!, $series: String!, $countOfPages: Int!,
                $language: String!, $edition: String!, $author: String!, $categoryId: Int!,
                $description: String!, $imageId: Int!, $isPublic: Boolean!){
                editBookData(bookId: $Id, bookInput:{
                    title: $title, translator: $translator, series: $series, countOfPages: $countOfPages,
                     language: $language, edition: $edition, author: $author, 
                     categoryId: $categoryId, description: $description, imageId: $imageId, isPublic: $isPublic 
                }){
                    ok
                }
            }
        '''
        image_id = 0
        if edited_book_data['image']:
            image_id = DataQuery.upload_book_image_link(edited_book_data['image'])
        edited_book_data['categoryId'] = DataQuery.get_or_create_category_for_book(category_data=category_data)
        edited_book_data['imageId'] = DataQuery.upload_book_image_link(edited_book_data['image'])
        edited_book_data['Id'] = book_id
        print(edited_book_data)
        del edited_book_data['image']
        result = schema.execute(query, variables=edited_book_data)
        print(result)

    @staticmethod
    def change_books_visibility(change_visibility_info: dict):
        query = '''
            mutation change_book_visibility($bookId: Int!, $userId: Int!, $reason: String!, $canBookChangePublic: Boolean!){
                changeBookVisibility(bookId:$bookId, userId: $userId, reason: $reason, canBookChangePublic: $canBookChangePublic){
                    ok
                }
            }
        '''
        result = schema.execute(query, variables=change_visibility_info)

    @staticmethod
    def delete_book(book_id: int, user_id: int) -> bool:
        query = '''
            mutation delete_book($bookId: Int!, $userId: Int!){
                deleteBook(bookId:$bookId, userId: $userId){
                    ok
                }
            }
        '''
        result = schema.execute(query, variables={'bookId': book_id, 'userId': user_id}).data
        return result['deleteBook']['ok']

    @staticmethod
    def search_books(title: str, author: str, category_id: int) -> int:
        query = '''
            query search_books($title: String!, $author: String!, $categoryId: Int!){
                searchBooks(title:$title, author:$author, categoryId:$categoryId){
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
        result = schema.execute(query, variables={"title": title, "author": author, "categoryId": category_id}).data['searchBooks']
        Util.create_full_url_of_book_image_and_files(result)
        return result
