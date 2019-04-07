# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import werkzeug
import itertools
from odoo import http
from odoo import fields
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.osv.orm import browse_record
from odoo.tools.translate import _

class QueryURL(object):
    def __init__(self, path='', path_args=None, **args):
        self.path = path
        self.args = args
        self.path_args = set(path_args or [])

    def __call__(self, path=None, path_args=None, **kw):
        path = path or self.path
        for k, v in self.args.items():
            kw.setdefault(k, v)
        path_args = set(path_args or []).union(self.path_args)
        paths, fragments = [], []
        for key, value in kw.items():
            if value and key in path_args:
                if isinstance(value, browse_record):
                    paths.append((key, slug(value)))
                else:
                    paths.append((key, value))
            elif value:
                if isinstance(value, list) or isinstance(value, set):
                    fragments.append(werkzeug.url_encode([(key, item) for item in value]))
                else:
                    fragments.append(werkzeug.url_encode([(key, value)]))
        for key, value in paths:
            path += '/' + key + '/%s' % value
        if fragments:
            path += '?' + '&'.join(fragments)
        return path


class WebsiteBlog(http.Controller):
    _blog_post_home = 6
    _blog_post_per_page = 20
    _post_comment_per_page = 10

    def nav_list(self, blog=None):
        dom = blog and [('blog_id', '=', blog.id)] or []
        if not request.env.user.has_group('website.group_website_designer'):
            dom += [('post_date', '<=', fields.Datetime.now())]
        groups = request.env['blog.post']._read_group_raw(
            dom,
            ['name', 'post_date'],
            groupby=["post_date"], orderby="post_date desc")
        for group in groups:
            (r, label) = group['post_date']
            start, end = r.split('/')
            group['post_date'] = label
            group['date_begin'] = fields.Date.to_string(self._to_date(start))
            group['date_end'] = fields.Date.to_string(self._to_date(end))
            group['month'] = self._to_date(start).strftime("%B")
            group['year'] = self._to_date(start).strftime("%Y")
        return {year: [m for m in months] for year, months in itertools.groupby(groups, lambda g: g['year'])}

    def _to_date(self, dt):
        return fields.Date.from_string(dt)

    @http.route(['/blog_posts',], type='json', auth="public", website=True)
    def blog_posts(self, page=1, **post):
        blog_obj = request.env['blog.post']
        total = blog_obj.search([])
        if request.env.user.has_group('website.group_website_designer'):
            post_ids = blog_obj.search([], offset=(page-1)*self._blog_post_home, limit=self._blog_post_home, order="write_date desc")
        else:
            post_ids = blog_obj.search([("website_published", "=", True)], offset=(page-1)*self._blog_post_home, limit=self._blog_post_home, order="write_date desc")
        post_data = {}
        for post in post_ids:
            blog_url = "/blog/" + slug(post.blog_id) + "/post/" + slug(post)
            post_data[str(post.id)] = {
                'id_str': post.id,
                'title': post.name,
                'bg_img': post.background_image,
                'created_date': post.create_date,
                'blog_url': blog_url,
            }
        return post_data

    @http.route(['/blog/<model("blog.blog"):blog>/feed'], type='http', auth="public")
    def blog_feed(self, blog, limit='15'):
        v = {}
        v['blog'] = blog
        v['base_url'] = request.env['ir.config_parameter'].get_param('web.base.url')
        v['posts'] = request.env['blog.post'].search([('blog_id','=', blog.id)], limit=min(int(limit), 50))
        r = request.render("website_blog.blog_feed", v, headers=[('Content-Type', 'application/atom+xml')])
        return r

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: