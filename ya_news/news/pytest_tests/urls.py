from django.urls import reverse


class URLs:

    @staticmethod
    def home():
        return reverse('news:home')

    @staticmethod
    def detail(news_id):
        return reverse('news:detail', args=(news_id,))

    @staticmethod
    def edit(comment_id):
        return reverse('news:edit', args=(comment_id,))

    @staticmethod
    def delete(comment_id):
        return reverse('news:delete', args=(comment_id,))

    @staticmethod
    def login():
        return reverse('users:login')

    @staticmethod
    def logout():
        return reverse('users:logout')

    @staticmethod
    def signup():
        return reverse('users:signup')
