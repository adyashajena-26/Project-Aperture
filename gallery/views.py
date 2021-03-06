from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse

from pdfs.utils import similar_captions
from .models import Picture, Tag, Caption
from .forms import PictureForm
from .utils import generate_tags, reverse_image_generate_tags, correct_spell_and_meaning, find_similar_tags, generate_caption, find_similar_captions
import random
import base64, io

# Create your views here.
# import random
# alpha = []
# for i in range(26):
#     alpha += [chr(ord('a')+ i)]

# def generate(n):
#     res = []
#     for i in range(n):
#         n = random.randint(3,8)
#         string =  ''.join(random.sample(alpha,k=n))
#         res+= [string]
#     return res

TOTAL_IMAGES = len(list(Picture.objects.all()))
TOTAL_PAGES = TOTAL_IMAGES//50

def url_generator(im):
    b = io.BytesIO()
    im.save(b, format='PNG')
    b = b.getvalue()
    b64_im = base64.b64encode(b)
    image_url = u'data:img/jpeg;base64,'+b64_im.decode('utf-8')
    return image_url

def contributeImageView(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PictureForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                obj = Picture(image=image)
                obj.save()

                generated_tags = generate_tags(obj.image.url)
                more_tags, captions = generate_caption(obj.image.url)
                generated_tags = list(set(generated_tags).union(set(more_tags)))
                new_tags = []
                new_captions = []
                for tag in generated_tags:
                    if not Tag.objects.filter(tag_name = tag).exists():
                        new_tag = Tag(tag_name = tag)
                        new_tag.save()
                        new_tags.append(new_tag)
                    else:
                        t = Tag.objects.get(tag_name = tag)
                        new_tags.append(t)
                for tag in new_tags:
                    obj.tag.add(tag)

                for cap in captions:
                    if not Caption.objects.filter(description = cap).exists():
                        new_cap = Caption(description = cap)
                        new_cap.save()
                        new_captions.append(new_cap)
                    else:
                        c = Caption.objects.get(description = cap)
                        new_captions.append(c)
                
                for captions in new_captions:
                    obj.caption.add(captions)

                return redirect("edit_image", image_id=obj.id)
        else:
            form = PictureForm()
        context = {
            'form' : form,
        }

        return render(request, 'pages/image_contribute.html', context=context)
    else:
        return redirect('login')

def multiple_image_upload(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            images = request.FILES.getlist('uploaded_images')
            final_image_id = []
            for image in images:
                obj = Picture(image=image)
                obj.save()
                generated_tags = generate_tags(obj.image.url)
                more_tags, captions = generate_caption(obj.image.url)
                generated_tags = list(set(generated_tags).union(set(more_tags)))
                new_tags = []
                new_captions = []
                for tag in generated_tags:
                    if not Tag.objects.filter(tag_name = tag).exists():
                        new_tag = Tag(tag_name = tag)
                        new_tag.save()
                        new_tags.append(new_tag)
                    else:
                        t = Tag.objects.get(tag_name = tag)
                        new_tags.append(t)
                for tag in new_tags:
                    obj.tag.add(tag)

                for cap in captions:
                    if not Caption.objects.filter(description = cap).exists():
                        new_cap = Caption(description = cap)
                        new_cap.save()
                        new_captions.append(new_cap)
                    else:
                        c = Caption.objects.get(description = cap)
                        new_captions.append(c)
                
                for captions in new_captions:
                    obj.caption.add(captions)
                final_image_id.append(str(obj.id))

            
            return redirect('multi-edit-page', slug='-'.join(final_image_id))
    else:
        return redirect('login')

def delete_tag_multiple(request, slug, tag_id, image_id):
    if request.user.is_authenticated:
        tag = Tag.objects.get(id=tag_id)
        pic = Picture.objects.get(id=image_id)
        pic.tag.remove(tag)
        return redirect("multi-edit-page", slug=slug)
    else:
        return redirect('login')

def add_tag_multiple(request, slug, image_id):
    if request.user.is_authenticated:
        image = Picture.objects.get(id=image_id)
        new_tag_name = request.POST['new_tag'].lower()
        if not Tag.objects.filter(tag_name = new_tag_name).exists():
            tag = Tag(tag_name = new_tag_name)
            tag.save()
            image.tag.add(tag)
            return redirect("multi-edit-page", slug=slug)
        else:
            tag = Tag.objects.get(tag_name = new_tag_name)
            image.tag.add(tag)
            return redirect("multi-edit-page", slug=slug)
        
    else:
        return redirect('login')

def multi_edit_page_view(request, slug):
    if request.user.is_authenticated:
        image_ids = list(map(int, slug.split("-")))
        pics = []
        for id in image_ids:
            pics.append(Picture.objects.get(id=id))

        context = {
            'images': pics,
            'slug': slug
        }
        return render(request, 'pages/after_multiple_upload.html', context=context)
    else:
        return redirect('login')

def after_upload_view(request, image_id):
    if request.user.is_authenticated:
        context = {
            'img': Picture.objects.get(id=image_id)
        }
        return render(request, 'pages/edit_tags_intermediate.html', context=context)
    return redirect("login")

def homepage(request):
    if request.user.is_authenticated:
        page_no = None
        try:
            page_no = int(request.GET['pg'])
            pics = list(Picture.objects.all())
            pics = pics[50*(page_no-1): 50*(page_no-1)+50]
        except:
            pics = list(Picture.objects.all())
            random.shuffle(pics)
        context = {
            'img': pics[:50],
            'pages': [i+1 for i in range(TOTAL_PAGES)],
            'page_no': page_no
        }
        return render(request, 'pages/landing_page.html', context=context)
    return redirect('login')

def recently_uploaded_view(request):
    if request.user.is_authenticated:
        pics = list(Picture.objects.all())
        pics = pics[::-1]
        context = {
            'img': pics[:20]
        }
        return render(request, 'pages/landing_page.html', context=context)
    return redirect('login')

def single_image_view(request, image_id):
    if request.user.is_authenticated:
        image = Picture.objects.get(id=image_id)
        caption = image.caption.all()[0]
        similar_captions = find_similar_captions(caption.description)
        similar_images = []
        for i in range(len(similar_captions)):
            similar_images.append(list(Caption.objects.filter(description = similar_captions[i]))[0].picture_set.all()[0])
        image.count_view+=1
        image.save()
        context = {
            'img': image,
            'tags': image.tag.all(),
            'similar_images': set(similar_images[0:10])
        }
        return render(request, 'pages/single_view.html', context=context)
    return redirect("login")

def delete_tag_from_image(request, tag_id, image_id):
    if request.user.is_authenticated:
        img = Picture.objects.get(id=image_id)
        tag = Tag.objects.get(id=tag_id)
        img.tag.remove(tag)
        return redirect("edit_image", image_id=image_id)
    return redirect("login")

def add_tag_to_image(request, image_id):
    if request.user.is_authenticated:
        img = Picture.objects.get(id = image_id)
        new_tag_name = request.POST['new_tag']
        if not Tag.objects.filter(tag_name = new_tag_name).exists():
            tag = Tag(tag_name = new_tag_name)
            tag.save()
            img.tag.add(tag)
            return redirect("edit_image", image_id=image_id)
        else:
            tag = Tag.objects.get(tag_name = new_tag_name)
            img.tag.add(tag)
            return redirect("edit_image", image_id=image_id)
    else:
        return redirect("login")

def update_caption(request, image_id):
    if request.user.is_authenticated:
        updated_caption = request.POST['updated_caption']
        if len(updated_caption) == 0:
            return redirect("edit_image", image_id=image_id)
        else:
            img = Picture.objects.get(id=image_id)
            caption = list(img.caption.all())[0]
            if len(caption.picture_set.all())>1:
                new_cap = Caption(description = updated_caption)
                new_cap.save()
                img.caption.remove(caption)
                img.caption.add(new_cap)
            else:
                caption.description = updated_caption
                caption.save()
            return redirect("edit_image", image_id=image_id)
    else:
        return redirect('login')

def tag_based_image_search(request):
    if request.user.is_authenticated:
        search = request.GET['search_tag'].lower()
        corrected_search = correct_spell_and_meaning(search)
        corrected_flag = False
        if len(corrected_search.split(" "))>=2:    
            context = caption_based_search(corrected_search)
            if corrected_search != search:
                corrected_flag = True
                context['DidYouMean'] = corrected_search
            context['corrected_flag'] = corrected_flag
            context['searched_for'] = search
            return render(request, 'pages/caption_search.html', context=context)
        related_tags = find_similar_tags(corrected_search)
        search_keywords = corrected_search.split(" ")
        image_not_found = False
        img = []
        for word in search_keywords:
            tag = Tag.objects.filter(tag_name__startswith = word)
            for t in tag:
                img += list(t.picture_set.all())
        if len(img) == 0:
            image_not_found = True
        if corrected_search!=search:
            corrected_flag = True
        context = {
                'img': set(img),
                'related_tags': related_tags[1:],
                'searched_for': search,
                'corrected_flag': corrected_flag,
                'DidYouMean': corrected_search,
                'image_not_found': image_not_found
            }
        return render(request, 'pages/search_results.html', context=context)
    else:
        return redirect('login')

def caption_based_search(search):
    similar_captions = find_similar_captions(search)
    related_captions = []
    for i in range(20):
        g = Caption.objects.filter(description=similar_captions[i])
        if len(g)>=1:
            related_captions.append(list(g)[0])
        # else:
        #     related_captions.append(g)
    
    img = []
    for cap in related_captions:
        for i in cap.picture_set.all():
            img.append(i)
    context = {
        'img': img
    }
    return context


def tag_click_search(request, tag_id):
    if request.user.is_authenticated:
        tag = Tag.objects.get(id=tag_id)
        related_tags = find_similar_tags(tag.tag_name)
        context = {
            'img': tag.picture_set.all(),
            'related_tags': related_tags[1:],
            'searched_for': tag.tag_name
        }
        return render(request, 'pages/tag_click_search.html', context=context)
    else:
        return redirect('login')

def reverse_image_search(request):
    if request.user.is_authenticated:
        if 'search_image' in request.FILES:
            image = request.FILES['search_image']
            generated_tags = reverse_image_generate_tags(image)
            img = []
            db_tags = []
            for t in generated_tags:
                if Tag.objects.filter(tag_name = t).exists():
                    db_tags.append(Tag.objects.get(tag_name = t))
            for tag in generated_tags:
                out = Tag.objects.filter(tag_name__startswith = tag)
                for t in out:
                    img += list(t.picture_set.all())
            if len(img) == 0:
                return HttpResponse("Image kichi nahin")
            else:
                context = {
                    'img': set(img),
                    'generated_tags': db_tags
                }
                return render(request, 'pages/search_results.html', context=context)
        else:
            print("ethiki asuchi")
            return redirect('/')
    else:
        return redirect('login')

def trending_image_view(request):
    if request.user.is_authenticated:
        pics = list(Picture.objects.all().order_by('-count_view'))
        context = {
            'img': pics[:20]
        }
        return render(request, 'pages/landing_page.html', context=context)
    else:
        return redirect('login')

def tag_analytics_dashboard(request):
    if request.user.is_authenticated:
        tags = list(Tag.objects.all())
        total_tags = len(tags)
        recent_tags = tags[total_tags-50:]
        most_used = sorted(tags, key=lambda x: len(x.picture_set.all()))[total_tags-50:]
        context = {
            'tags': tags,
            'total_tags': total_tags,
            'recent_tags': recent_tags,
            'most_used_tags': most_used[::-1]
        }
        return render(request, 'pages/tag_analytics.html', context=context)
    else:
        return redirect('login')
    