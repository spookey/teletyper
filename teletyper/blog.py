from logging import getLogger
from pprint import pformat
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
        if self.__info is None:
            self.log.debug(
                'request blog info for "%s"', self.conf.tumblr_blog_name
            )
            self.__info = [
                blog for blog in self.client.info()['user']['blogs']
                if blog['name'] == self.conf.tumblr_blog_name
            ][-1]
        return self.__info

    def log_post(self, post, text):
        self.log.info('\n    '.join([
            'tumblr post ->', text, '\n',
            pformat(post.get('posts')),
        ]))

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
        self.log_post(post, 'photo')
        return self.client.posts(
            self.info['name'], id=post['id']
        ).get('posts', [None])[0]

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
        self.log_post(post, 'video')
        return self.client.posts(
            self.info['name'], id=post['id']
        ).get('posts', [None])[0]
