import os
import numpy as np
from django.shortcuts import render
from django.http import JsonResponse
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from django.conf import settings

# Load the model once when the server starts to avoid reloading
MODEL_PATH = os.path.join(settings.BASE_DIR, 'predictor/static/models/my_model.keras')
model = load_model(MODEL_PATH)
CLASS_LABELS = ['Damaged', 'Green', 'Red', 'Yellow']

def predict_tomato(request):
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_file = request.FILES['image']
        
        # Save the uploaded file temporarily
        temp_file_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        with open(temp_file_path, 'wb+') as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
        
        # Preprocess the image
        img = image.load_img(temp_file_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0

        # Make a prediction
        prediction = model.predict(img_array)
        predicted_class = CLASS_LABELS[np.argmax(prediction)]

        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        # Return the result as JSON
        return JsonResponse({
            'predicted_class': predicted_class,
            'probabilities': prediction.tolist()[0]
        })
    
    return render(request, 'home.html')
