from datetime import datetime
from logging import getLogger
from requests import get
from dateutil import parser
from youtube_dl import YoutubeDL

from teletyper.lib.disk import (
    destroy_location, ensured_folder, ensured_parent_folder, walk_location,
    write_json, join_location, check_location
)


class Pull(object):
    def __init__(self, conf, blog, vlog):
        self.log = getLogger(__name__)
        self.conf = conf
        self.blog = blog
        self.vlog = vlog
        self.loc = dict(
            files=ensured_parent_folder(self.conf.pull_folder, 'files.json'),
            photos=ensured_folder(self.conf.pull_folder, 'photos'),
            videos=ensured_folder(self.conf.pull_folder, 'videos'),
            ydl_da=ensured_parent_folder(
                self.conf.pull_folder, '.youtube_dl_download_archive'
            ),
        )
        self.ydl_opts = dict(
            download_archive=self.loc['ydl_da'],
            format='best',
            logger=getLogger('youtube_dl'),
        )

    def __element(self, prime, ext, url, *, tags, text, time, short=None):
        time = time.strftime(self.conf.post_title_fmt)
        return prime, dict(
            href=short if short else url,
            tags=['#{}'.format(tag) for tag in tags],
            text=text if text else '', time=time, url=url,
            file='{}_{}.{}'.format(time, prime, ext)
        )

    def _pull_photos(self):
        for post in self.blog.pull_photos():
            if post['state'] == 'published':
                yield self.__element(
                    post['id'], 'jpg',
                    post['photos'][0]['original_size']['url'],
                    short=post['short_url'],
                    tags=post['tags'],
                    text=post['summary'],
                    time=datetime.fromtimestamp(post['timestamp'])
                )

    def _pull_videos(self):
        for post in self.vlog.pull_videos():
            if post['status'] == 'available':
                yield self.__element(
                    post['uri'].split('/')[-1], 'm4v',
                    post['link'],
                    tags=[tag['canonical'] for tag in post['tags']],
                    text=post['description'],
                    time=parser.parse(post['created_time'])
                )

    def _load_photo(self, url, location):
        if check_location(location, folder=False):
            return True
        self.log.info('downloading photo "%s" "%s"', location, url)
        request = get(url, stream=True)
        if request.status_code == 200:
            with open(location, 'wb') as handle:
                for chunk in request:
                    handle.write(chunk)
                return True
        self.log.error(
            'photo download error "%s" "%s" "%s"', vars(request), location, url
        )

    def _load_video(self, url, location):
        self.log.info('downloading video "%s" "%s"', location, url)
        with YoutubeDL(dict(outtmpl=location, **self.ydl_opts)) as ydl:
            ydl.download([url])
            return True
        self.log.error(
            'video download error "%s" "%s" "%s"', vars(ydl), location, url
        )

    def __call__(self):
        result = dict(
            time=datetime.utcnow().strftime(self.conf.post_title_fmt)
        )
        for main, pull_func, load_func in [
                ('photos', self._pull_photos, self._load_photo),
                ('videos', self._pull_videos, self._load_video)
        ]:
            result[main] = dict()
            content = dict(pull_func())
            files = [elem['file'] for elem in content.values()]
            for elem in walk_location(self.loc[main]):
                if elem.inner not in files:
                    destroy_location(elem.full)
            for key, elem in content.items():
                if load_func(
                        elem['url'],
                        join_location(self.loc[main], elem['file'])
                ):
                    result[main][key] = elem

        write_json(self.loc['files'], content=result)
        return True
