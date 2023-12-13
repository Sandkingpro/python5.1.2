import csv
import json

from django.http import HttpResponse
from django.shortcuts import render, reverse, redirect
from datetime import datetime
from .forms import ImageForm
from app.neuralnnetwork import predict, to_array
import os
import cv2
import numpy as np


def time_view(request):
    current_time = datetime.now().strftime("%H:%M:%S")
    msg = f'Текущее время: {current_time}'
    return HttpResponse(msg)


def workdir_view(request):
    template_name = 'app/directory.html'
    files = os.listdir(os.getcwd())
    context = {
        'files': files
    }
    return render(request, template_name, context)


def image_upload_view(request):
    """Process images uploaded by users"""
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Get the current instance object to display in the template
            img_obj = form.instance
            # Получить путь к сохраненному файлу
            img_path = img_obj.image.path

            # Загрузить изображение с помощью OpenCV
            img = cv2.imread(img_path)
            prediction = predict(img)
            return render(request, 'app/home.html',
                          {'form': form, 'img_obj': img_obj, 'prediction': prediction})
    else:
        form = ImageForm()
    return render(request, 'app/home.html', {'form': form})


def set_class(request):
    if request.method == 'POST':
        selected_digit = int(request.POST.get('action'))
        img_path = request.POST.get('img_path')
        img = cv2.imread(img_path)
        img_data = to_array(img)
        new_array = np.array([np.append(img_data, selected_digit)])

        destination_path = os.path.join('media/images', 'incorrect', 'labels.txt')
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        with open(destination_path, 'a') as file:
            np.savetxt(file, new_array, fmt='%d', newline='\n')

    return redirect('image_upload_view')


def process_image(request):
    if request.method == 'POST':
        action = request.POST.get('action', '')
        img_path = request.POST.get('img_path', '')
        prediction = request.POST.get('prediction', '')
        if action == 'correct':
            # Move image to the 'correct' folder
            new_path = move_image(img_path, 'correct')
            img = cv2.imread(new_path)
            img_data = to_array(img)
            new_array = np.array([np.append(img_data, int(prediction))])

            destination_path = os.path.join('media/images', 'correct', 'labels.txt')
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            with open(destination_path, 'a') as file:
                np.savetxt(file, new_array, fmt='%d', newline='\n')
        elif action == 'incorrect':
            # Move image to the 'incorrect' folder
            new_path = move_image(img_path, 'incorrect')
            return render(request, 'app/classes.html',
                          {'img_path': new_path})

        return redirect('image_upload_view')


def move_image(img_path, destination_folder):
    # Прочитать изображение с использованием OpenCV
    img = cv2.imread(img_path)

    # Определить путь к новой директории
    destination_path = os.path.join('media/images', destination_folder)

    # Создать директорию, если она не существует
    os.makedirs(destination_path, exist_ok=True)

    # Получить новый путь для изображения
    new_path = os.path.join(destination_path, os.path.basename(img_path))

    # Переместить изображение
    os.rename(img_path, new_path)
    cv2.imwrite(new_path, img)
    return new_path
