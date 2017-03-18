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

    def get(self, *uri, **param):
        url = '/{}'.format('/'.join(uri).lstrip('/'))
        self.log.debug('request vlog info "%s"', url)
        req = self.client.get(url, **param)
        res = req.json()
        if req.status_code != 200:
            self.log.warning('vlog info error response "%s"', res)
            return
        return res

    def quota(self, size):
        info = self.get('me')
        if info:
            return info['upload_quota']['space']['free'] > size

    def upload(self, source):
        res = self.client.post('/me/videos', data=dict(
            type='pull', link=source
        ))
        video = res.json()
        if res.status_code != 200:
            self.log.error('video upload error "%s"', video)
            return
        return video

    def change(self, video, *, title, caption, public, tags=[]):
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
        return video

    def pull_videos(self):
        for offset in range(1, self.get('me', 'videos').get('total', 1), 25):
            for post in self.get(
                    'me', 'videos', data=dict(page=offset)
            )['data']:
                yield post
