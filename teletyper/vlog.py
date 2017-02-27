from logging import getLogger

from vimeo import VimeoClient


class Vlog(object):
    def __init__(self, conf, blog):
        self.log = getLogger(__name__)
        self.conf = conf
        self.blog = blog

        self.client = VimeoClient(
            token=self.conf.vimeo_token,
            key=self.conf.vimeo_client_id,
            secret=self.conf.vimeo_client_secret
        )

    @property
    def info(self):
        res = self.client.get('/me')
        return res.json() if res.status_code == 200 else {}

    def check_quota(self, size):
        return self.info['upload_quota']['space']['free'] > size

    def post_video(self, source, *, title, caption, public, tags=[]):
        res = self.client.post('/me/videos', data=dict(
            type='pull', link=source
        ))
        video = res.json()
        if res.status_code != 200:
            self.log.error('video upload error "%s"', video)
            return

        res = self.client.patch(video['uri'], data=dict(
            name=title,
            description=caption,
            privacy=dict(
                embed='public',
                view=('anybody' if public else 'nobody'),
            )
        ))
        if res.status_code != 200:
            self.log.error('video edit error "%s"', res.json())
            return

        res = self.client.put('{}/tags'.format(video['uri']), data=tags)
        if res.status_code not in [200, 201]:
            self.log.error('video tag error "%s"', res.json())
            return

        return video['embed']['html']
