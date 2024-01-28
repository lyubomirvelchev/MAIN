from django.shortcuts import render


def article_list(request):
    return render(request, "article/article_list.html")
