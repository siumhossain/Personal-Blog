from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect
from . models import Post,Comment
from django.core.paginator import Paginator, EmptyPage,\
PageNotAnInteger
from . forms import EmailPostForm,CommentForm
from django.core.mail import send_mail

# Create your views here.


def home(request,tag_slug=None):
    post = Post.objects.all()
    paginator = Paginator(post,3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
# If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
# If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    return render(request,'home.html',
        {   'page':page,
            'posts':post}
    )

def post_detail(request, year, month, day, post):
        post = get_object_or_404(Post, slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day)
    # List of active comments for this post
        comments = post.comments.filter(active=True)
        new_comment = None
        if request.method == 'POST':
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.post = post
                new_comment.save()
        else:
            comment_form = CommentForm()
        post_tags_id = Post.tags.values_list('id',flat=True)
        context = {
            'post':post,
            'comments':comments,
            'new_comment':new_comment,
            'comment_form':comment_form
            
        }
        return render(request,'detail.html',context)
    
    

def post_share(request,post_id):
    post = get_object_or_404(Post,id=post_id,status='published')
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
            post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
            f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
            f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'pika29404@gmail.com',
            [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request,'share.html',{'post':post,
    'form':form,'sent': sent}
    )


