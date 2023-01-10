
from yatube.settings import NUMBER_POST
from django.core.paginator import Paginator


def page_paginator(request, posts):
    paginator = Paginator(posts, NUMBER_POST)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
