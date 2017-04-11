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

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)



class handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(handler):
    def get(self):
        self.redirect("/blog")

class blogPost(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class Blog(handler):
    def renderFront(self):
        blogPosts = db.GqlQuery("""
                                SELECT * FROM blogPost
                                ORDER BY created DESC
                                LIMIT 5
                                """)

        return self.render("front.html", blogPosts=blogPosts)

    def get(self):
        self.renderFront()


class NewPost(handler):
    def renderNewPost(self, title="", post="", error=""):
        return self.render("newpost.html", title=title, post=post, error=error)

    def get(self):
        self.renderNewPost()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            b = blogPost(title = title, body = post)
            b.put()
            self.redirect("/blog/" + str(b.key().id()))
        else:
            error = "You need a title and a post!"
            self.renderNewPost(title=title, post=post, error=error)

class ViewPostHandler(handler):
    def get(self, id):
        post = blogPost.get_by_id(int(id))

        if post:
            self.response.write(post)
        else:
            error="Sorry, but we can't find that post."
            self.response.write(error)

        self.render("viewpost.html", post = post)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', Blog),
    ('/new-post', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
