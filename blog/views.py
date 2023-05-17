from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Count
from django.db.models import Prefetch



def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments.count(),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }




def serialize_tag(tag):
    return {
        'title': tag.title,
        # 'posts_with_tag': Post.objects.prefetch_related(Prefetch("tags", queryset=
        # Tag.objects.annotate(Count("posts")))).count,


        'posts_with_tag': tag.posts.count,

        # 'posts_with_tag': len(Post.objects.filter(tags=tag)),


    }


def index(request):
    most_fresh_posts = Post.objects.prefetch_related('author').prefetch_related('tags').order_by('-published_at')[:5]

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in Post.objects.popular().prefetch_related('author')[:5]
            .fetch_with_comments_count()
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    all_posts = Post.objects.prefetch_related('author').prefetch_related('tags').annotate(likes_count=Count('likes'))
    post = all_posts.get(slug=slug)
    comments = Comment.objects.filter(post=post)
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    related_tags = post.tags.all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes.count(),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in Post.objects.popular().prefetch_related('author')[:5]
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]

    related_posts = tag.posts.all()[:20]

    related_posts_ids = [post.id for post in related_posts]

    related_posts_with_comments = Post.objects.filter(id__in=related_posts_ids).annotate(
        comments_count=Count('comments'))

    related_ids_and_comments = related_posts_with_comments.values_list('id', 'comments_count')

    related_count_for_id = dict(related_ids_and_comments)

    for post in related_posts:
        post.comments_count = related_count_for_id[post.id]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in Post.objects.popular().prefetch_related('author')[:5]
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
