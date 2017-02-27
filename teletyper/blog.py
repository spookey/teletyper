from logging import getLogger

from pytumblr import TumblrRestClient


class Blog(object):
    def __init__(self, conf):
        self.log = getLogger(__name__)
        self.conf = conf
        self.__info = None

        self.client = TumblrRestClient(
            self.conf.tumblr_consumer_key,
            self.conf.tumblr_consumer_secret,
            self.conf.tumblr_oauth_token,
            self.conf.tumblr_oauth_secret
        )
        self.log.debug('%s init done', __name__)

    @property
    def info(self):
        if not self.__info:
            self.log.debug(
                'request blog info for "%s"', self.conf.tumblr_blog_name
            )
            self.__info = [
                blog for blog in self.client.info()['user']['blogs']
                if blog['name'] == self.conf.tumblr_blog_name
            ][-1]
        return self.__info

    def post_photo(self, source, *, title, caption, public, tags=[]):
        post = self.client.create_photo(
            self.info['name'],
            caption=caption,
            format='markdown',
            slug=title,
            source=source,
            state=('published' if public else 'draft'),
            tags=tags
        )
        return self.client.posts(self.info['name'], id=post['id'])['posts'][0]

    def post_video(self, embed, *, title, caption, public, tags=[]):
        post = self.client.create_video(
            self.info['name'],
            caption=caption,
            embed=embed,
            format='markdown',
            slug=title,
            state=('published' if public else 'draft'),
            tags=tags
        )
        return self.client.posts(self.info['name'], id=post['id'])['posts'][0]
