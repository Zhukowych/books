<template>
    <div class="col-md-3">
       <div class="card mb-4 shadow-sm">
          <img :src="book.image" class="card-img-top" style="height: 300px;" alt="">
          <div class="card-body">
             <a :href="resolveBookUrl(book.id)"><strong class="card-text">{{ book.title }}</strong></a>
             <div class="d-flex justify-content-between align-items-center">
                <small class="text-muted">Категорія: <strong><a :href="resolveCategoryUrl(book.category.id)">{{ book.category.name }}</a></strong></small>
             </div>

             <a v-if="user_id===book.uploadAuthor.id" :href="resolveEditBookUrl(book.id)" class="btn btn-sm btn-outline-secondary">Редагувати</a>
             <a v-if="has_perm==='True'" class="btn btn-sm btn-outline-danger" :href="resolveAdminEditBookUrl(book.id)">Змінити статус</a>
             <br>
             <a v-for="file in book.referencedBookFile" :href="file.file">{{ file.expansion }} |</a>

          </div>
       </div>
    </div>
</template>
<script>
    export default {
        name:"book",
        props:['book', 'user_id', 'has_perm'],
        methods:{
            resolveBookUrl(bookId) {
                return "http://127.0.0.1:8000/book/" + bookId + "/";
            },
            resolveCategoryUrl(categoryId) {
                return "http://127.0.0.1:8000/category/" + categoryId;
            },
            resolveEditBookUrl(bookId){
                return "http://127.0.0.1:8000/edit_book/" + bookId + "/";
            },
            resolveAdminEditBookUrl(bookId){
                return "http://127.0.0.1:8000/admin_edit_book/" + bookId + "/";
            },
        }
    }
</script>