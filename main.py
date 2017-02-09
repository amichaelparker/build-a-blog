#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

def get_posts(limit, offset):
    posts = db.GqlQuery('SELECT * FROM BlogPost \
                        ORDER BY created DESC \
                        LIMIT ' + str(limit) + ' OFFSET ' + str(offset))
    return posts

class BlogPost(db.Model):
    title = db.StringProperty()#required = True)
    post = db.TextProperty()#required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        data = BlogPost()
        post_id = data.get_by_id(int(id))
        if not post_id:
            self.redirect('/blog')
        else:
            t = jinja_env.get_template('post.html')
            content = t.render(title = post_id.title, post = post_id.post)
            self.response.write(content)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect('/blog')

class RecentPosts(webapp2.RequestHandler):
    def get(self):
        page = self.request.get('page')

        if not page:
            page = 1

        offset = 0
        for _ in range(int(page) - 1):
            offset += 5


        posts = get_posts(5, offset)

        t = jinja_env.get_template('blog.html')
        content = t.render(posts = posts, offset = offset, page = int(page))
        self.response.write(content)

class NewPost(webapp2.RequestHandler):
    def get(self, title="", post="", error=""):
        t = jinja_env.get_template('newpost.html')
        content = t.render(title = title, blogpost = post, error = error)
        self.response.write(content)

    def post(self):
        title = self.request.get('title')
        post = self.request.get('blogpost')

        if title and post:
            p = BlogPost(title = title, post = post)
            p.put()
            post_re = p.key().id()
            self.redirect('/blog/' + str(post_re))
        else:
            error = "Please fill out both Title and Post fields."
            self.get(title, post, error)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', RecentPosts),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
