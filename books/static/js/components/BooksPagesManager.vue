<template>
    <div>
        <div class="d-flex justify-content-between align-items-center">
            <p v-on:click="pageDown"><--</p>
            <p>1 - <strong>{{page+1}}</strong> - {{getMaxPage()}}</p>
            <p v-on:click="pageUp">--></p>
        </div>
        <div class="row">
            <book v-for="book in current_books" v-bind:key="book.id" v-bind:book="book" v-bind:user_id="user_id" v-bind:has_perm="has_perm"></book>
        </div>
    </div>
</template>
<script>
    import Book from './Book.vue'
    const BOOKS_PER_PAGE = 8;
    export default {
        components:{
            'book': Book
        },
        data(){
            return{
                all_books: JSON.parse($(".book_data").text()),
                current_books: JSON.parse($(".book_data").text()).slice(0, BOOKS_PER_PAGE),
                user_id: $('.user_id').text(),
                has_perm: $('.has_perm').text(),
                page:0
            }
        },
        methods:{
            getMaxPage: function() {
                let page_count = Math.floor(this.all_books.length / BOOKS_PER_PAGE)
                if(this.all_books.length%BOOKS_PER_PAGE > 0)
                    page_count ++;
                if(page_count==0)
                    page_count = 1;
                return page_count;
            },
            pageUp: function() {
                if (this.getMaxPage() != this.page+1) {
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
                this.current_books = this.all_books.slice(start, end);
            }
        }
    }
</script>