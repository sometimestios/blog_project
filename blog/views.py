from django.shortcuts import render, get_object_or_404
from .models import Post, Category, Tag
import markdown
import re
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify
from django.views.generic import ListView, DetailView


# 继承了django自带的ListView
class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'


# 继承了IndexView
class ArchiveView(IndexView):
    def get_queryset(self):
        return super(ArchiveView, self).get_queryset().filter(created_time__year=self.kwargs.get('year'),
                                                              created_time__month=self.kwargs.get('month'))


class CategoryView(IndexView):

    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)


class TagView(IndexView):
    def get_queryset(self):
        ta = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tag=ta)


def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.increase_views()
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            TocExtension(slugify=slugify),
        ])
    post.body = md.convert(post.body)
    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    post.toc = m.group(1) if m is not None else ''
    return render(request, 'blog/detail.html', context={'post': post})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        self.object.increase_views()
        return response

    def get_object(self, queryset=None):
        post = super(PostDetailView, self).get_object(queryset=None)
        md = markdown.Markdown(
            extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                TocExtension(slugify=slugify)])
        post.body = md.convert(post.body)
        # 将下面post.body替换成md.toc可以在文章没有添加[TOC]的情况下显示目录
        m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>',post.body, re.S)
        post.toc = m.group(1) if m is not None else ''
        return post