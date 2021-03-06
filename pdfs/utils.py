import PyPDF2
import random
from PIL import Image
from django.conf import settings
import os

from .models import PDF_Caption
from gallery.utils import sentence_similarity_model
from sklearn.metrics.pairwise import cosine_similarity


alpha = []
for i in range(26):
    alpha += [chr(ord('a') + i)]


def generate():
    string = ''.join(random.sample(alpha, k=5))
    return string


def make_custom_file_name_jpg(file_name):
    while True:
        print(file_name)
        if os.path.exists(os.path.join(file_name)):
            aux = generate()
            file_name = file_name.split('.')[0] + '_' + aux + '.jpg'
        else:
            return file_name


def make_custom_file_name_png(file_name):
    while True:
        print(file_name, "asuchi")
        if os.path.exists(os.path.join(file_name)):
            aux = generate()
            file_name = file_name.split('.')[0] + '_' + aux + '.png'
        else:
            return file_name


def extract_images(file_path):
    absolute_path = str(settings.BASE_DIR) + file_path
    print(absolute_path)
    pdf_file = PyPDF2.PdfFileReader(open(absolute_path, "rb"))
    new_files = []
    for i in range(pdf_file.numPages):
        page = pdf_file.getPage(i)
        try:
            xObject = page['/Resources']['/XObject'].getObject()

            for obj in xObject:
                if xObject[obj]['/Subtype'] == '/Image':
                    size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                    data = xObject[obj]._data
                    if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                        mode = "RGB"
                    else:
                        mode = "P"
                    if xObject[obj]['/Filter'] == '/FlateDecode':
                        try:
                            img = Image.frombytes(mode, size, data)
                            file_name = 'extracted_images/'+obj[1:] + ".png"
                            file_name = make_custom_file_name_png(file_name)
                            new_files.append(file_name)
                            print(file_name, "changed")
                            img.save(file_name)
                            img.close()
                        except:
                            pass
                    elif xObject[obj]['/Filter'] == '/DCTDecode':
                        try:
                            file_name = 'extracted_images/'+obj[1:] + ".jpg"
                            file_name = make_custom_file_name_jpg(file_name)
                            new_files.append(file_name)
                            print(file_name, "changed")
                            img = open(file_name, "wb")
                            img.write(data)
                            img.close()
                        except:
                            pass
        except:
            pass
    return new_files


def similar_captions(searched_caption):
    all_captions = list(PDF_Caption.objects.all(
    ).values_list('description', flat=True))
    all_captions_vecs = sentence_similarity_model.encode(all_captions)
    searched_vec = sentence_similarity_model.encode([searched_caption])
    similarities = cosine_similarity(searched_vec, all_captions_vecs)
    vectors_with_similarity_factor = [
        [similarities[0][i], all_captions[i]] for i in range(len(similarities[0]))]
    vectors_with_similarity_factor = sorted(
        vectors_with_similarity_factor, key=lambda x: x[0], reverse=True)
    sorted_captions = [i[1] for i in vectors_with_similarity_factor]
    return sorted_captions
