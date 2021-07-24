from facebook_scraper import get_posts
class FB_page():

    no_of_posts = 2
    def __init__(self, page_name):
        self.name   = page_name
        self.text   = None
        self.date   = None
        self.video  = None
        self.images = None
        self.link   = None
        self.cached_post_time = None

    def load_next(self, next_post):

        self.text   = next_post['text']
        self.date   = next_post['time']
        self.video  = next_post['video']
        self.images = next_post['images']
        self.link   = next_post['link']

    def have_post(self):
        if self.text is not None or self.images is not None or self.video is not None:
            return True
        else:
            return False

    def get_new_posts(self):
        new_posts = []
        # Change IP every request
        # IP.change_IP()
        cashed_posts = get_posts(self.name)

        for i in range(0, self.no_of_posts):  # will send last few posts since last cached post time
            next_post = next(cashed_posts)
            if next_post is None:
                break

            if i == 0:
                first_post = next_post
                next_post = next(cashed_posts)
                if first_post['time'] > next_post['time']:  # no pin post
                    if self.cached_post_time is not None:
                        if first_post['time'] <= self.cached_post_time:  # no new post on top
                            break
                    new_posts.append(first_post)
                    if self.cached_post_time is None:
                        break

                else:  # there is a Pin post
                    while first_post['time'] < next_post['time']:
                        first_post = next_post
                        try:
                            next_post = next(cashed_posts)
                        except:
                            break

                    next_post = first_post

                    if self.cached_post_time is None:
                        new_posts.append(next_post)
                        break

            if next_post['time'] > self.cached_post_time:  # more posts newer than last cached post
                new_posts.append(next_post)
            else:
                break

        if len(new_posts) > 0:
            self.cached_post_time = new_posts[0]['time']
        return new_posts

    def reset_page(self):
        self.cached_post_time = None
        self.delete_cached_post()

    def delete_cached_post(self):
        self.text = None
        self.video = None
        self.images = None
        self.link = None