const BOOKS_PER_PAGE = 8;

Vue.component("book", {
    props: ['book'],
    template:'   <div class="col-md-3" v-for="book in current_page_books">\n' +
        '      <div class="card mb-4 shadow-sm">\n' +
        '         <img :src="(( book.image ))" class="card-img-top" style="height: 300px;" alt="">\n' +
        '         <div class="card-body">\n' +
        '             <a :href=""><strong class="card-text">(( book.title ))</strong></a><br>\n' +
        '             <div class="d-flex justify-content-between align-items-center">\n' +
        '               <small class="text-muted">Категорія: <strong><a :href="">((book.category.name))</a></strong></small>\n' +
        '            </div>\n' +
        '            <a href="" v-if="user_id===book.uploadAuthor.id" class="btn btn-sm btn-outline-secondary">Редагувати</a>\n' +
        '            <a class="btn btn-sm btn-outline-danger" href="" v-if="has_perm===\'True\'">Змінити статус</a><br>\n' +
        '            <a v-for="file in book.referencedBookFile" href="file.file">(( file.expansion )) |</a>\n' +
        '         </div>\n' +
        '      </div>\n' +
        '   </div>',
    delimiters: ['((', '))']
})


var app = new Vue({
    el: '.pages_block',
    data: {
        view: false,
        all_books: JSON.parse($(".books_data").text()),
        current_page_books: JSON.parse($(".books_data").text()).slice(0, BOOKS_PER_PAGE),
        user_id: user_id_,
        has_perm: if_has_perm,
        page: 0
    },
    methods: {

        resolveBookUrl(bookId) {
            return "http://127.0.0.1:8000/book/" + bookId + "/";
        },
        resolveCategoryUrl(categoryId) {
            return "http://127.0.0.1:8000/category/" + categoryId;
        },
        pageUp: function() {
            if ((Math.floor(this.all_books.length / BOOKS_PER_PAGE)) != this.page) {
                this.page++;
                this.change_viewed_books();
            }
        },
        pageDown: function() {
            if (this.page != 0) {
                this.page--;
                this.change_viewed_books();
            }
        },
        change_viewed_books: function() {
            let start = this.page * BOOKS_PER_PAGE;
            let end = start + BOOKS_PER_PAGE;
            if (end > this.all_books.length) {
                end = this.all_books.length;
            }
            this.current_page_books = this.all_books.slice(start, end);
        },
        getMaxPage: function() {
            return (Math.floor(this.all_books.length / BOOKS_PER_PAGE) + this.all_books.length % BOOKS_PER_PAGE);
        }
    },
    delimiters: ['((', '))']
})